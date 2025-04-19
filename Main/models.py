from django.db import models
from django.core.validators import MinValueValidator
from tinymce.models import HTMLField
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from habanero import Crossref
from django.utils.functional import cached_property

# User Model
class Profile(models.Model):
    """
    User Profile model for storing additional user information
    One-to-one relationship with Django's built-in User model
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User'
    )
    
    # Basic information
    bio = models.TextField(blank=True, verbose_name='Biography')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Phone Number'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Birth Date'
    )
    
    # Academic information
    academic_degree = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Academic Degree'
    )
    field_of_study = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Field of Study'
    )
    university = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='University'
    )
    
    # Settings
    email_confirmed = models.BooleanField(
        default=False,
        verbose_name='Email Confirmed'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user__username']

    def __str__(self):
        return f'Profile of {self.user.username}'

# Signal to automatically create profile when a new user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create/update user profile automatically
    when user is created/updated
    """
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# 0-Public model
class Keyword(models.Model):
    """
    Model for storing research keywords/tags
    Used for categorizing and searching projects
    """
    term = models.CharField(max_length=100, verbose_name='Keyword', unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Keyword'
        verbose_name_plural = 'Keywords'
        ordering = ['term']

    def __str__(self):
        return self.term

class Author(models.Model):
    """
    Model for storing author information (separate from User model)
    """
    # Personal information
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    email = models.EmailField(verbose_name='Email', blank=True)
    orcid_id = models.CharField(
        max_length=19, 
        blank=True, 
        verbose_name='ORCID ID',
        help_text='Format: XXXX-XXXX-XXXX-XXXX'
    )
    
    # Academic information
    affiliation = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Affiliation'
    )
    researcher_id = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name='Researcher ID'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        ordering = ['last_name', 'first_name']
        unique_together = ['first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    full_name.short_description = 'Full Name'

class Project(models.Model):
    """
    Main research project model
    Represents different types of academic/research projects
    """
    # Project owner (researcher/student)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Project Owner'
    )

    # Project type choices
    PROJECT_TYPES = (
        ('article_writing', 'Article Writing'),
        ('book_writing', 'Book Writing'),
        ('book_translation', 'Book Translation'),
        ('research_proposal', 'Research Proposal'),
        ('research_project', 'Research Project'),
        ('thesis', 'Thesis/Dissertation'),
    )
    
    # Project status choices
    PROJECT_STATUS = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('published', 'Published'),
        ('canceled', 'Canceled'),
    )
    
    # Core project fields
    title = models.CharField(max_length=200, verbose_name='Project Title')

    description = models.TextField(verbose_name='Description', blank=True)
    type = models.CharField(
        max_length=100,
        choices=PROJECT_TYPES,
        verbose_name='Project Type'
    )
    status = models.CharField(
        max_length=100,
        choices=PROJECT_STATUS,
        default='not_started',
        verbose_name='Project Status'
    )
    
    # Timeline fields
    start_date = models.DateField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateField(verbose_name='End Date', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Relationships
    keywords = models.ManyToManyField(
        Keyword,
        related_name='projects',
        blank=True,
        verbose_name='Keywords'
    )

    related_projects = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Related Projects',
        help_text='Projects related to this one'
    )

    tags = models.ManyToManyField(
        'ProjectTag',
        blank=True,
        verbose_name='Project Tags'
    )

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    @cached_property
    def project_output(self):
        """
        Returns the specific output object related to this project
        (e.g., Article for article_writing projects)
        Uses cached_property for better performance
        """
        try:
            if self.type == 'article_writing':
                return self._article
            elif self.type == 'book_writing':
                return self._book
            elif self.type == 'book_translation':
                return self.translated_book
            elif self.type == 'research_proposal':
                return self.research_proposal
            elif self.type == 'research_project':
                return self.research_project
            elif self.type == 'thesis':
                return self.thesis
        except:
            return None
        


class Task(models.Model):
    """
    Model for project tasks/milestones
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Project'
    )
    
    # Task details
    title = models.CharField(max_length=200, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    due_date = models.DateField(null=True, blank=True, verbose_name='Due Date')
    completed = models.BooleanField(default=False, verbose_name='Completed')

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['due_date']

    def __str__(self):
        return f"Task: {self.title} ({self.project.title})"


class ProjectComment(models.Model):
    """
    Model for comments/discussion on projects
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Project'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    
    # Comment content
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Project Comment'
        verbose_name_plural = 'Project Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.project.title}"


class ProjectTag(models.Model):
    """
    Model for tagging/categorizing projects
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Tag Name')
    color = models.CharField(
        max_length=7, 
        default='#007bff',  # Default blue color
        verbose_name='Color Code (HEX)'
    )
    
    class Meta:
        verbose_name = 'Project Tag'
        verbose_name_plural = 'Project Tags'
        ordering = ['name']

    def __str__(self):
        return self.name



# 1-Article Models
class Article(models.Model):
    """
    Enhanced Article model with improved structure for academic writing
    """
    ARTICLE_TYPES = (
        ('research', 'Research Article'),
        ('review', 'Review Article'),
        ('analytical', 'Analytical Article'),
        ('descriptive', 'Descriptive Article'),
        ('theoretical', 'Theoretical Article'),
        ('short', 'Short Communication'),
        ('survey', 'Survey Article'),
        ('narrative', 'Narrative Article'),
        ('editorial', 'Editorial'),
        ('practical', 'Practical Article'),
    )
    
    ARTICLE_STATUS = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('accepted', 'Accepted'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )
    
    # Link to parent project (must be article_writing type)
    project = models.OneToOneField(
        'Project',
        on_delete=models.SET_NULL,
        related_name='article',
        limit_choices_to={'type': 'article_writing'},
        null=True,
        blank=True,
        verbose_name='Related Project'
    )
    
    # Core Metadata
    article_type = models.CharField(
        max_length=100,
        choices=ARTICLE_TYPES,
        verbose_name='Article Type'
    )
    title = models.CharField(max_length=300, verbose_name='Article Title')
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Subtitle'
    )
    abstract = models.TextField(blank=True, verbose_name='Abstract')
    keywords = models.ManyToManyField(
        Keyword,
        related_name='articles',
        blank=True,
        verbose_name='Keywords'
    )
    authors = models.ManyToManyField(
        Author,
        related_name='authored_articles',
        verbose_name='Authors',
        through='ArticleAuthorship'
    )
    
    # Publication Information
    status = models.CharField(
        max_length=50,
        choices=ARTICLE_STATUS,
        default='draft',
        verbose_name='Status'
    )
    journal = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Journal/Conference'
    )
    volume = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Volume'
    )
    issue = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Issue'
    )
    pages = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Pages'
    )
    doi = models.CharField(
        max_length=100, 
        verbose_name='DOI', 
        blank=True,
        unique=True
    )
    is_published = models.BooleanField(default=False, verbose_name='Published')
    publish_date = models.DateField(
        verbose_name='Publish Date', 
        null=True, 
        blank=True
    )
    
    # Files
    manuscript = models.FileField(
        upload_to='articles/manuscripts/',
        null=True,
        blank=True,
        verbose_name='Manuscript File'
    )
    supplementary_materials = models.FileField(
        upload_to='articles/supplementary/',
        null=True,
        blank=True,
        verbose_name='Supplementary Materials'
    )
    
    # Timestamps
    submitted_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Submitted Date'
    )
    accepted_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Accepted Date'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-publish_date', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_article_type_display()})"

    def get_authors_display(self):
        """Returns formatted string of authors"""
        return ", ".join([author.get_full_name() for author in self.authors.all()])

    def get_citation(self):
        """Generates a standard citation for the article"""
        authors = self.get_authors_display()
        year = self.publish_date.year if self.publish_date else "n.d."
        title = self.title
        journal = f"{self.journal}" if self.journal else ""
        volume = f", {self.volume}" if self.volume else ""
        issue = f"({self.issue})" if self.issue else ""
        pages = f", {self.pages}" if self.pages else ""
        doi = f", https://doi.org/{self.doi}" if self.doi else ""
        
        return f"{authors} ({year}). {title}. {journal}{volume}{issue}{pages}{doi}"

    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    def create_from_template(self, template_id):
        """Create article sections from a template"""
        template = ArticleTemplate.objects.get(id=template_id)
        for section in template.sections.all().order_by('default_position'):
            ArticleSection.objects.create(
                article=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position
            )

class ArticleAuthorship(models.Model):
    """
    Through model for Article-Author relationship with authorship details
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        verbose_name='Article'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    is_corresponding = models.BooleanField(
        default=False,
        verbose_name='Corresponding Author'
    )
    authorship_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Authorship Order'
    )
    affiliation = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Affiliation for this work'
    )
    contributions = models.TextField(
        blank=True,
        verbose_name='Author Contributions'
    )

    class Meta:
        verbose_name = 'Article Authorship'
        verbose_name_plural = 'Article Authorships'
        ordering = ['authorship_order']
        unique_together = ('article', 'author')

    def __str__(self):
        return f"{self.author.get_full_name()} in {self.article.title}"


class ArticleSection(models.Model):
    """
    Model for different sections of an article
    Each section type has its own required fields
    """
    SECTION_TYPES = (
        # Common sections
        ('title', 'Title'),
        ('abstract', 'Abstract'),
        ('keywords', 'Keywords'),
        ('introduction', 'Introduction'),
        ('references', 'References'),
        
        # Research Method sections
        ('stimuli', 'Stimuli'),
        ('subject', 'Subject'),
        ('procedure', 'Procedure'),
        ('data acquisition and analysis', 'Data acquisition and analysis'),
        
        # Research  sections
        ('results', 'Results'),
        ('discussion', 'Discussion'),
        ('conclusion', 'Conclusion'),
        
        # Analytical article sections
        ('analysis', 'In-depth Analysis'),
        ('arguments', 'Logical Arguments'),
        
        # Review article sections
        ('literature_review', 'Literature Review'),
        ('synthesis', 'Synthesis'),
        
        # Other specialized sections
        ('case_study', 'Case Study'),
        ('implications', 'Practical Implications'),
        ('limitations', 'Limitations'),
        ('acknowledgments', 'Acknowledgments'),
    )
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Article'
    )
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Section Title'
    )
    content = HTMLField(verbose_name='Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Article'
    )
    
    # For reference sections
    references = models.ManyToManyField(
        'Reference',
        blank=True,
        verbose_name='Cited References'
    )
    
    class Meta:
        verbose_name = 'Article Section'
        verbose_name_plural = 'Article Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.article.title}"
    
class ArticleTemplate(models.Model):
    """
    Predefined templates for different article types
    """
    ARTICLE_TYPES = Article.ARTICLE_TYPES
    
    name = models.CharField(max_length=100, verbose_name='Template Name')
    article_type = models.CharField(
        max_length=100,
        choices=ARTICLE_TYPES,
        verbose_name='Article Type'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    
    sections = models.ManyToManyField(
        'ArticleTemplateSection',
        related_name='templates',
        verbose_name='Sections'
    )
    
    class Meta:
        verbose_name = 'Article Template'
        verbose_name_plural = 'Article Templates'
        
    def __str__(self):
        return f"{self.name} ({self.get_article_type_display()})"


class ArticleTemplateSection(models.Model):
    """
    Sections for article templates
    """
    SECTION_TYPES = ArticleSection.SECTION_TYPES
    
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Default Title'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description/Guidance'
    )
    required = models.BooleanField(
        default=True,
        verbose_name='Required Section'
    )
    default_position = models.PositiveIntegerField(
        default=0,
        verbose_name='Default Position'
    )
    
    class Meta:
        verbose_name = 'Template Section'
        verbose_name_plural = 'Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"
    

# 2- Book model 
class BookChapter(models.Model):
    """
    Model for chapters in a book (for both Book and TranslatedBook)
    """
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='Book',
        null=True,
        blank=True
    )
    translated_book = models.ForeignKey(
        'TranslatedBook',
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='Translated Book',
        null=True,
        blank=True
    )
    
    chapter_number = models.PositiveIntegerField(verbose_name='Chapter Number')
    title = models.CharField(max_length=200, verbose_name='Chapter Title')
    summary = models.TextField(blank=True, verbose_name='Chapter Summary')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Book Chapter'
        verbose_name_plural = 'Book Chapters'
        ordering = ['chapter_number']
        constraints = [
            models.CheckConstraint(
                check=models.Q(book__isnull=False) | models.Q(translated_book__isnull=False),
                name='chapter_must_belong_to_book_or_translated_book'
            )
        ]

    def __str__(self):
        book_title = self.book.project.title if self.book else self.translated_book.project.title
        return f"Chapter {self.chapter_number}: {self.title} ({book_title})"


class BookSection(models.Model):
    """
    Model for sections within a book chapter
    """
    SECTION_TYPES = (
        ('text', 'Text'),
        ('figure', 'Figure'),
        ('table', 'Table'),
        ('quote', 'Quote'),
        ('list', 'List'),
        ('code', 'Code'),
        ('equation', 'Equation'),
        ('footnote', 'Footnote'),
    )
    
    chapter = models.ForeignKey(
        BookChapter,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Chapter'
    )
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Section Title'
    )
    content = HTMLField(verbose_name='Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Chapter'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Translator/Author Notes'
    )
    
    class Meta:
        verbose_name = 'Book Section'
        verbose_name_plural = 'Book Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.chapter.title}"


class BookFigure(models.Model):
    """
    Model for figures in books
    """
    chapter = models.ForeignKey(
        BookChapter,
        on_delete=models.CASCADE,
        related_name='figures',
        verbose_name='Chapter'
    )
    title = models.CharField(max_length=200, verbose_name='Figure Title')
    description = models.TextField(blank=True, verbose_name='Description')
    image = models.ImageField(
        upload_to='book_figures/',
        verbose_name='Image File'
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Chapter'
    )
    source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Source/Credit'
    )

    class Meta:
        verbose_name = 'Book Figure'
        verbose_name_plural = 'Book Figures'
        ordering = ['position']

    def __str__(self):
        return f"Figure: {self.title} ({self.chapter.title})"

class BookTable(models.Model):
    """
    Model for tables in books
    """
    chapter = models.ForeignKey(
        BookChapter,
        on_delete=models.CASCADE,
        related_name='tables',
        verbose_name='Chapter'
    )
    title = models.CharField(max_length=200, verbose_name='Table Title')
    content = HTMLField(verbose_name='Table Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Chapter'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        verbose_name = 'Book Table'
        verbose_name_plural = 'Book Tables'
        ordering = ['position']

    def __str__(self):
        return f"Table: {self.title} ({self.chapter.title})"

class Book(models.Model):
    """
    Model for books produced in book_writing projects
    """
    # Link to parent project (must be book_writing type)
    project = models.OneToOneField(
        'Project',
        on_delete=models.CASCADE,
        related_name='_book',
        limit_choices_to={'type': 'book_writing'}
    )
    
    # Book metadata
    publisher = models.CharField(max_length=200, verbose_name='Publisher')
    publish_date = models.DateField(verbose_name='Publish Date', null=True, blank=True)
    isbn = models.CharField(max_length=100, verbose_name='ISBN', blank=True)
    page_count = models.PositiveIntegerField(verbose_name='Page Count', null=True, blank=True)
    authors = models.TextField(verbose_name='Authors')
    edition = models.PositiveIntegerField(verbose_name='Edition', default=1)
    is_published = models.BooleanField(default=False, verbose_name='Published')
    
    # Book structure fields
    preface = HTMLField(verbose_name='Preface', blank=True)
    introduction = HTMLField(verbose_name='Introduction', blank=True)
    conclusion = HTMLField(verbose_name='Conclusion', blank=True)
    bibliography = HTMLField(verbose_name='Bibliography', blank=True)
    index = HTMLField(verbose_name='Index', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['-created_at']

    def __str__(self):
        return f"Book: {self.project.title}"

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def total_chapters(self):
        """Returns total number of chapters"""
        return self.chapters.count()

class TranslatedBook(models.Model):
    """
    Model for translated books produced in book_translation projects
    """
    # Link to parent project (must be book_translation type)
    project = models.OneToOneField(
        'Project',
        on_delete=models.CASCADE,
        related_name='translated_book',
        limit_choices_to={'type': 'book_translation'}
    )
    
    # Translation metadata
    original_title = models.CharField(max_length=200, verbose_name='Original Title')
    original_language = models.CharField(max_length=100, verbose_name='Original Language')
    publisher = models.CharField(max_length=200, verbose_name='Publisher')
    publish_date = models.DateField(verbose_name='Publish Date', null=True, blank=True)
    isbn = models.CharField(max_length=100, verbose_name='ISBN', blank=True)
    page_count = models.PositiveIntegerField(verbose_name='Page Count', null=True, blank=True)
    translator = models.CharField(max_length=200, verbose_name='Translator')
    original_author = models.CharField(max_length=200, verbose_name='Original Author')
    is_published = models.BooleanField(default=False, verbose_name='Published')
    
    # Translation structure fields
    translator_preface = HTMLField(verbose_name='Translator Preface', blank=True)
    original_preface = HTMLField(verbose_name='Original Preface', blank=True)
    introduction = HTMLField(verbose_name='Introduction', blank=True)
    conclusion = HTMLField(verbose_name='Conclusion', blank=True)
    bibliography = HTMLField(verbose_name='Bibliography', blank=True)
    index = HTMLField(verbose_name='Index', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Translated Book'
        verbose_name_plural = 'Translated Books'
        ordering = ['-created_at']

    def __str__(self):
        return f"Translated Book: {self.project.title}"

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def total_chapters(self):
        """Returns total number of chapters"""
        return self.chapters.count()

class BookReference(models.Model):
    """
    Model for references cited in books
    """
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='references',
        verbose_name='Book',
        null=True,
        blank=True
    )
    translated_book = models.ForeignKey(
        TranslatedBook,
        on_delete=models.CASCADE,
        related_name='references',
        verbose_name='Translated Book',
        null=True,
        blank=True
    )
    
    reference = models.ForeignKey(
        'Reference',
        on_delete=models.CASCADE,
        verbose_name='Reference'
    )
    citation_text = models.TextField(verbose_name='Citation Text', blank=True)
    page_number = models.CharField(max_length=100, verbose_name='Page Number', blank=True)
    
    class Meta:
        verbose_name = 'Book Reference'
        verbose_name_plural = 'Book References'
        constraints = [
            models.CheckConstraint(
                check=models.Q(book__isnull=False) | models.Q(translated_book__isnull=False),
                name='reference_must_belong_to_book_or_translated_book'
            )
        ]

    def __str__(self):
        book_title = self.book.project.title if self.book else self.translated_book.project.title
        return f"Reference in {book_title}: {self.reference.title}"

# 3-Research Proposal Models
class ResearchProposal(models.Model):
    """
    Model for research proposals produced in research_proposal projects
    Contains detailed sections of a research proposal
    """
    # Link to parent project (must be research_proposal type)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='research_proposal',
        limit_choices_to={'type': 'research_proposal'}
    )
    
    # Basic info
    name_fa = models.CharField(max_length=200, verbose_name='Persian Name')
    name_en = models.CharField(max_length=200, verbose_name='English Name')
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Budget',
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    duration_months = models.PositiveIntegerField(
        verbose_name='Duration (months)',
        null=True,
        blank=True
    )
    sponsor = models.CharField(max_length=200, verbose_name='Sponsor', blank=True)

    # Content sections (using HTMLField for rich text)
    problem_statement = HTMLField(verbose_name='Problem Statement', blank=True)
    research_importance = HTMLField(verbose_name='Research Importance', blank=True)
    literature_review = HTMLField(verbose_name='Literature Review', blank=True)
    research_objectives = HTMLField(verbose_name='Research Objectives', blank=True)
    research_methodology = HTMLField(verbose_name='Research Methodology', blank=True)
    expected_results = HTMLField(verbose_name='Expected Results', blank=True)
    references_section = HTMLField(verbose_name='References', blank=True)


    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    def create_from_template(self, template_id):
        """Create proposal sections from a template"""
        template = ResearchProposalTemplate.objects.get(id=template_id)
        for section in template.sections.all().order_by('default_position'):
            ResearchProposalSection.objects.create(
                proposal=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position
            )

    class Meta:
        verbose_name = 'Research Proposal'
        verbose_name_plural = 'Research Proposals'

    def __str__(self):
        return f"Research Proposal: {self.project.title}"
    

class ResearchProposalSection(models.Model):
    """
    Model for sections of a research proposal
    """
    SECTION_TYPES = (
        ('title', 'Title Page'),
        ('abstract', 'Abstract'),
        ('introduction', 'Introduction'),
        ('problem_statement', 'Problem Statement'),
        ('research_questions', 'Research Questions'),
        ('objectives', 'Objectives'),
        ('significance', 'Significance of Research'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('research_design', 'Research Design'),
        ('data_collection', 'Data Collection Methods'),
        ('data_analysis', 'Data Analysis Methods'),
        ('timeline', 'Timeline/Schedule'),
        ('budget', 'Budget'),
        ('expected_outcomes', 'Expected Outcomes'),
        ('references', 'References'),
        ('appendices', 'Appendices'),
    )
    
    proposal = models.ForeignKey(
        ResearchProposal,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Research Proposal'
    )
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Section Title'
    )
    content = HTMLField(verbose_name='Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Proposal'
    )
    
    class Meta:
        verbose_name = 'Research Proposal Section'
        verbose_name_plural = 'Research Proposal Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.proposal.project.title}"


class ResearchProposalTemplate(models.Model):
    """
    Template for research proposals with predefined sections
    """
    name = models.CharField(max_length=100, verbose_name='Template Name')
    description = models.TextField(blank=True, verbose_name='Description')
    disciplines = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Applicable Disciplines'
    )
    
    sections = models.ManyToManyField(
        'ResearchProposalTemplateSection',
        related_name='templates',
        verbose_name='Sections'
    )
    
    class Meta:
        verbose_name = 'Research Proposal Template'
        verbose_name_plural = 'Research Proposal Templates'

    def __str__(self):
        return self.name


class ResearchProposalTemplateSection(models.Model):
    """
    Predefined sections for research proposal templates
    """
    SECTION_TYPES = ResearchProposalSection.SECTION_TYPES
    
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Default Title'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description/Guidance'
    )
    required = models.BooleanField(
        default=True,
        verbose_name='Required Section'
    )
    default_position = models.PositiveIntegerField(
        default=0,
        verbose_name='Default Position'
    )
    
    class Meta:
        verbose_name = 'Proposal Template Section'
        verbose_name_plural = 'Proposal Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"
    
# 4-Research Project Models
class ResearchProjectSection(models.Model):
    """
    Model for different sections of a research project
    """
    SECTION_TYPES = (
        # Methodology sections
        ('title', 'title'),
        ('research_design', 'Research Design'),
        ('participants', 'Participants'),
        ('materials', 'Materials/Instruments'),
        ('procedure', 'Procedure'),
        ('data_collection', 'Data Collection'),
        ('data_analysis', 'Data Analysis'),
        ('ethical_considerations', 'Ethical Considerations'),
        
     )
    
    research_project = models.ForeignKey(
        'ResearchProject',
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Research Project'
    )
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Section Title'
    )
    content = HTMLField(verbose_name='Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Project'
    )
    
    class Meta:
        verbose_name = 'Research Project Section'
        verbose_name_plural = 'Research Project Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.research_project.project.title}"


class ResearchProject(models.Model):
    """
    Model for research projects produced in research_project projects
    """
    # Link to parent project (must be research_project type)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='research_project',
        limit_choices_to={'type': 'research_project'}
    )
    
    # Research project metadata
    organization = models.CharField(max_length=200, verbose_name='Organization')
    research_code = models.CharField(max_length=50, verbose_name='Research Code', blank=True)
    supervisor = models.CharField(max_length=100, verbose_name='Supervisor', blank=True)
    research_team = models.TextField(verbose_name='Research Team', blank=True)
     # For reference sections
    references = models.ManyToManyField(
        'Reference',
        blank=True,
        verbose_name='Cited References'
    )

    class Meta:
        verbose_name = 'Research Project'
        verbose_name_plural = 'Research Projects'

    def __str__(self):
        return f"Research Project: {self.project.title}"
    
    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

# 5-Thesis Models
class Thesis(models.Model):
    """
    Model for theses/dissertations produced in thesis projects
    """
    # Link to parent project (must be thesis type)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='thesis',
        limit_choices_to={'type': 'thesis'}
    )
    
    # Thesis metadata
    student_name = models.CharField(max_length=100, verbose_name='Student Name')
    university = models.CharField(max_length=200, verbose_name='University')
    department = models.CharField(max_length=200, verbose_name='Department', blank=True)
    defense_date = models.DateField(verbose_name='Defense Date', null=True, blank=True)
    supervisor = models.CharField(max_length=100, verbose_name='Supervisor')
    advisor = models.CharField(max_length=100, verbose_name='Advisor', blank=True)
    grade = models.CharField(max_length=50, verbose_name='Grade', blank=True)
    thesis_file = models.FileField(
        upload_to='theses/',
        verbose_name='Thesis File',
        null=True,
        blank=True
    )
    abstract = models.TextField(verbose_name='Abstract', blank=True)


    # اضافه کردن متدهای کمکی
    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def create_from_template(self, template_id):
        """Create thesis sections from a template"""
        template = ThesisTemplate.objects.get(id=template_id)
        for section in template.sections.all().order_by('default_position'):
            ThesisSection.objects.create(
                thesis=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position
            )

    class Meta:
        verbose_name = 'Thesis'
        verbose_name_plural = 'Theses'

    def __str__(self):
        return f"Thesis: {self.project.title}"
    


class ThesisSection(models.Model):
    """
    Model for sections of a thesis/dissertation
    """
    SECTION_TYPES = (
        ('title', 'Title Page'),
        ('approval', 'Approval Page'),
        ('dedication', 'Dedication'),
        ('acknowledgments', 'Acknowledgments'),
        ('abstract', 'Abstract'),
        ('table_of_contents', 'Table of Contents'),
        ('list_of_tables', 'List of Tables'),
        ('list_of_figures', 'List of Figures'),
        ('list_of_abbreviations', 'List of Abbreviations'),
        ('introduction', 'Introduction'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('results', 'Results'),
        ('discussion', 'Discussion'),
        ('conclusion', 'Conclusion'),
        ('recommendations', 'Recommendations'),
        ('references', 'References'),
        ('appendices', 'Appendices'),
    )
    
    thesis = models.ForeignKey(
        Thesis,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name='Thesis'
    )
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Section Title'
    )
    content = HTMLField(verbose_name='Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Thesis'
    )
    
    class Meta:
        verbose_name = 'Thesis Section'
        verbose_name_plural = 'Thesis Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.thesis.project.title}"


class ThesisChapter(models.Model):
    """
    Model for main chapters of a thesis (e.g., Literature Review, Methodology)
    """
    thesis = models.ForeignKey(
        Thesis,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='Thesis'
    )
    chapter_number = models.PositiveIntegerField(verbose_name='Chapter Number')
    title = models.CharField(max_length=200, verbose_name='Chapter Title')
    summary = models.TextField(blank=True, verbose_name='Chapter Summary')
    
    
    class Meta:
        verbose_name = 'Thesis Chapter'
        verbose_name_plural = 'Thesis Chapters'
        ordering = ['chapter_number']

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"


class ThesisTemplate(models.Model):
    """
    Template for theses with predefined structure
    """
    name = models.CharField(max_length=100, verbose_name='Template Name')
    description = models.TextField(blank=True, verbose_name='Description')
    university = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='University'
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Department'
    )
    
    sections = models.ManyToManyField(
        'ThesisTemplateSection',
        related_name='templates',
        verbose_name='Sections'
    )
    
    class Meta:
        verbose_name = 'Thesis Template'
        verbose_name_plural = 'Thesis Templates'

    def __str__(self):
        return f"{self.name} ({self.university})"


class ThesisTemplateSection(models.Model):
    """
    Predefined sections for thesis templates
    """
    SECTION_TYPES = ThesisSection.SECTION_TYPES
    
    section_type = models.CharField(
        max_length=100,
        choices=SECTION_TYPES,
        verbose_name='Section Type'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Default Title'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description/Guidance'
    )
    required = models.BooleanField(
        default=True,
        verbose_name='Required Section'
    )
    default_position = models.PositiveIntegerField(
        default=0,
        verbose_name='Default Position'
    )
    
    class Meta:
        verbose_name = 'Thesis Template Section'
        verbose_name_plural = 'Thesis Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"


# 100-Reference Management Models
class Reference(models.Model):
    """
    Base Reference model that connects to Article, Book, or Thesis
    """
    REFERENCE_TYPES = (
        ('article', 'Article'),
        ('book', 'Book'),
        ('thesis', 'Thesis'),
    )
    
    # Reference to one of the three types
    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPES,
        verbose_name='Reference Type'
    )
    
    # Links to the actual objects (only one will be non-null)
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Article Reference'
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Book Reference'
    )
    thesis = models.ForeignKey(
        'Thesis',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Thesis Reference'
    )
    
    # Common fields for all references
    citation_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Citation Key'
    )

    doi = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        unique=True,
        verbose_name='DOI'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_doi(cls, doi, project=None):
        """
        ایجاد یا بازیابی منبع بر اساس DOI
        """
        # بررسی وجود منبع با این DOI
        existing_ref = cls.objects.filter(doi=doi).first()
        if existing_ref:
            if project:
                # اگر پروژه مشخص شده، منبع را به آن اضافه کنید
                Citation.objects.get_or_create(project=project, reference=existing_ref)
            return existing_ref
        
        # اگر منبع وجود ندارد، از Crossref اطلاعات را دریافت کنید
        cr = Crossref()
        try:
            work = cr.works(ids=doi)
        except Exception as e:
            raise ValueError(f"خطا در دریافت اطلاعات از Crossref: {str(e)}")
        
        data = work['message']
        
        # ایجاد منبع جدید
        ref = cls(
            citation_key=f"doi_{doi}",
            reference_type='article',
            doi=doi,
            # سایر فیلدها بر اساس داده‌های Crossref
        )
        ref.save()
        
        # اگر پروژه مشخص شده، منبع را به آن اضافه کنید
        if project:
            Citation.objects.create(project=project, reference=ref)
        
        return ref
    
    class Meta:
        verbose_name = 'Reference'
        verbose_name_plural = 'References'
        ordering = ['citation_key']
        constraints = [
            models.CheckConstraint(
                check=models.Q(article__isnull=False) | 
                      models.Q(book__isnull=False) | 
                      models.Q(thesis__isnull=False),
                name='reference_must_have_one_source'
            )
        ]

    def __str__(self):
        return f"{self.citation_key} ({self.get_reference_type_display()})"

    def get_source(self):
        """
        Returns the actual referenced object
        """
        if self.article:
            return self.article
        elif self.book:
            return self.book
        elif self.thesis:
            return self.thesis
        return None

    def formatted_citation(self):
        """
        Generates citation based on the referenced object
        """
        source = self.get_source()
        if not source:
            return ""
            
        if self.reference_type == 'article':
            authors = ", ".join([author.get_full_name() for author in source.authors.all()])
            return f"{authors} ({source.publish_date.year}). {source.title}. {source.journal}, {source.volume}({source.issue}), {source.pages}."
        
        elif self.reference_type == 'book':
            return f"{source.authors} ({source.publish_date.year}). {source.title}. {source.publisher}."
        
        elif self.reference_type == 'thesis':
            return f"{source.student_name} ({source.defense_date.year}). {source.project.title}. {source.university}."
        
        return ""

class Citation(models.Model):
    """
    Model for tracking where references are cited in projects
    """
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='citations',
        verbose_name='Project'
    )
    
    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name='citations',
        verbose_name='Reference'
    )
    
    # Context of the citation
    citation_text = models.TextField(
        blank=True,
        verbose_name='Citation Text'
    )
    page_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Page Number'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Location in Document'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Citation'
        verbose_name_plural = 'Citations'
        unique_together = ('project', 'reference')

    def __str__(self):
        return f"Citation in {self.project.title} to {self.reference.citation_key}"

class ArticleReference(models.Model):
    """
    References used within an Article
    """
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='internal_references',
        verbose_name='Article'
    )
    
    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name='cited_in_articles',
        verbose_name='Reference'
    )
    
    context = models.TextField(
        blank=True,
        verbose_name='Citation Context'
    )
    
    class Meta:
        verbose_name = 'Article Reference'
        verbose_name_plural = 'Article References'
        unique_together = ('article', 'reference')

    def __str__(self):
        return f"Reference in {self.article.title} to {self.reference.citation_key}"

class BookReference(models.Model):
    """
    References used within a Book
    """
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='internal_references',
        verbose_name='Book'
    )
    
    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name='cited_in_books',
        verbose_name='Reference'
    )
    
    context = models.TextField(
        blank=True,
        verbose_name='Citation Context'
    )
    
    class Meta:
        verbose_name = 'Book Reference'
        verbose_name_plural = 'Book References'
        unique_together = ('book', 'reference')

    def __str__(self):
        return f"Reference in {self.book.project.title} to {self.reference.citation_key}"

class ThesisReference(models.Model):
    """
    References used within a Thesis
    """
    thesis = models.ForeignKey(
        'Thesis',
        on_delete=models.CASCADE,
        related_name='internal_references',
        verbose_name='Thesis'
    )
    
    reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name='cited_in_theses',
        verbose_name='Reference'
    )
    
    context = models.TextField(
        blank=True,
        verbose_name='Citation Context'
    )
    
    class Meta:
        verbose_name = 'Thesis Reference'
        verbose_name_plural = 'Thesis References'
        unique_together = ('thesis', 'reference')

    def __str__(self):
        return f"Reference in {self.thesis.project.title} to {self.reference.citation_key}"

