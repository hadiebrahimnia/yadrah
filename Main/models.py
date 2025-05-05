from django.db import models
from django.conf import settings
from django.urls import reverse
from tinymce.models import HTMLField
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.dispatch import receiver
from django.db.models.signals import post_save
import reversion
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

## User Models ##
class Profile(models.Model):
    """
    Enhanced User Profile model with additional academic fields
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='User'
    )
    
    # Basic information
    bio = models.TextField(blank=True, verbose_name='Biography')
    phone_number = models.CharField(max_length=15, blank=True, verbose_name='Phone Number')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Birth Date')
    
    # Academic information
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name='Academic Degree')
    field_of_study = models.CharField(max_length=100, blank=True, verbose_name='Field of Study')
    university = models.CharField(max_length=100, blank=True, verbose_name='University')
    department = models.CharField(max_length=100, blank=True, verbose_name='Department')
    position = models.CharField(max_length=100, blank=True, verbose_name='Position/Role')
    
    # Social/Professional links
    website = models.URLField(blank=True, verbose_name='Website')
    linkedin = models.URLField(blank=True, verbose_name='LinkedIn Profile')
    google_scholar = models.URLField(blank=True, verbose_name='Google Scholar Profile')
    researchgate = models.URLField(blank=True, verbose_name='ResearchGate Profile')
    
    # Settings
    email_confirmed = models.BooleanField(default=False, verbose_name='Email Confirmed')
    public_profile = models.BooleanField(default=False, verbose_name='Public Profile')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['user__username']

    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'username': self.user.username})

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


## Core Models ##

class Keyword(models.Model):
    term = models.CharField(max_length=100, verbose_name='Keyword', unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    def __str__(self):
        return self.term
    

class Author(models.Model):
    """
    Enhanced Author model with additional academic fields
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
    affiliation = models.CharField(max_length=200, blank=True, verbose_name='Affiliation')
    department = models.CharField(max_length=200, blank=True, verbose_name='Department')
    researcher_id = models.CharField(max_length=50, blank=True, verbose_name='Researcher ID')
    scopus_id = models.CharField(max_length=50, blank=True, verbose_name='Scopus Author ID')
    google_scholar_id = models.CharField(max_length=50, blank=True, verbose_name='Google Scholar ID')
    
    # Metadata
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='author_profile'
    )

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

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk': self.pk})
    



class Project(models.Model):
    """
    """
    # Project owner (researcher/student)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Project Owner'
    )
    
    # Visibility and collaboration
    visibility = models.CharField(
        max_length=10,
        choices=(
            ('public', 'Public'),
            ('private', 'Private'),
            ('team', 'Team Only'),
        ),
        default='private',
        verbose_name='Visibility'
    )
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='collaborated_projects',
        blank=True,
        verbose_name='Collaborators'
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
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=210, unique=True, blank=True)
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
        verbose_name='Status'
    )
    progress = models.IntegerField(
        choices=(
        (0, 'Not Started'),
        (25, '25% Completed'),
        (50, '50% Completed'),
        (75, '75% Completed'),
        (100, '100% Completed'),
        ),
        default=0,
        verbose_name='Progress'
    )
    
    # Timeline fields
    start_date = models.DateField(verbose_name='Start Date', null=True, blank=True)
    end_date = models.DateField(verbose_name='End Date', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    related_projects = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name='Related Projects',
        help_text='Projects related to this one'
    )

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        permissions = [
            ('can_invite_collaborators', 'Can invite collaborators'),
            ('can_change_visibility', 'Can change project visibility'),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    @property
    def is_public(self):
        return self.visibility == 'public'

    @property
    def is_private(self):
        return self.visibility == 'private'

    @property
    def is_team_only(self):
        return self.visibility == 'team'

    def can_view(self, user):
        if self.is_public:
            return True
        if not user.is_authenticated:
            return False
        if user == self.owner or user in self.collaborators.all():
            return True
        return False

    def can_edit(self, user):
        if not user.is_authenticated:
            return False
        return user == self.owner or user.has_perm('projects.change_project')

    def get_progress_class(self):
        if self.progress == 0:
            return 'danger'
        elif self.progress == 100:
            return 'success'
        return 'warning'
    



@reversion.register()
class Task(models.Model):
    """
    Enhanced Task model with priority and assignment
    """
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    project = models.ForeignKey( Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Project' )
    # Task details
    title = models.CharField(max_length=200, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')
    due_date = models.DateField(null=True, blank=True, verbose_name='Due Date')
    completed = models.BooleanField(default=False, verbose_name='Completed')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Assigned To'
    )
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name='Completed Date')

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['due_date']

    def __str__(self):
        return f"Task: {self.title} ({self.project.title})"

    def save(self, *args, **kwargs):
        if self.completed and not self.completed_date:
            self.completed_date = timezone.now()
        elif not self.completed and self.completed_date:
            self.completed_date = None
        super().save(*args, **kwargs)

@reversion.register()
class ProjectComment(models.Model):
    """
    Enhanced Comment model with threading and mentions
    """
    project = models.ForeignKey( Project, on_delete=models.CASCADE, related_name='comments', verbose_name='Project' )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    mentioned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='mentioned_in_comments',
        blank=True
    )
    
    # Comment content
    content = models.TextField(verbose_name='Content')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Project Comment'
        verbose_name_plural = 'Project Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.project.title}"

    def get_absolute_url(self):
        return reverse('comment_detail', kwargs={'pk': self.pk})

## Article Models ##

@reversion.register()
class Article(models.Model):
    """
    Enhanced Article model with comprehensive academic fields
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', verbose_name='Project' )
    title = models.CharField(max_length=500, verbose_name='Title')
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

    # Core Metadata
    article_type = models.CharField(
        max_length=100,
        choices=ARTICLE_TYPES,
        verbose_name='Article Type',
        blank=True,
    )
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='Subtitle')
    keywords = models.ManyToManyField(Keyword, blank=True, verbose_name='Keywords', related_name='articles')
    authors = models.ManyToManyField(
        Author,
        related_name='authored_articles',
        verbose_name='Authors',
        through='ArticleAuthorship'
    )
    
    # Publication Information
    aricale_status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('accepted', 'Accepted'),
            ('published', 'Published'),
            ('rejected', 'Rejected'),
        ),
        default='draft',
        verbose_name='Status'
    )
    journal = models.CharField(max_length=200, blank=True, verbose_name='Journal/Conference')
    volume = models.CharField(max_length=50, blank=True, verbose_name='Volume')
    issue = models.CharField(max_length=50, blank=True, verbose_name='Issue')
    pages = models.CharField(max_length=50, blank=True, verbose_name='Pages')
    doi = models.CharField(
        max_length=100, 
        verbose_name='DOI', 
        blank=True,
        unique=True
    )
    is_published = models.BooleanField(default=False, verbose_name='Published')
    publish_date = models.DateField(verbose_name='Publish Date', null=True, blank=True)
    
    # Citation metrics
    citation_count = models.PositiveIntegerField(default=0, verbose_name='Citation Count')
    download_count = models.PositiveIntegerField(default=0, verbose_name='Download Count')
    view_count = models.PositiveIntegerField(default=0, verbose_name='View Count')
    
    # Files
    manuscript = models.FileField(
        upload_to='articles/manuscripts/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Manuscript File'
    )
    supplementary_materials = models.FileField(
        upload_to='articles/supplementary/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Supplementary Materials'
    )
    
    # Timestamps
    submitted_date = models.DateField(null=True, blank=True, verbose_name='Submitted Date')
    accepted_date = models.DateField(null=True, blank=True, verbose_name='Accepted Date')
    
    # Template reference
    template = models.ForeignKey(
        'ArticleTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Article Template'
    )
    references = GenericRelation('Reference', content_type_field='cited_content_type', object_id_field='cited_object_id', related_query_name='articles')
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-publish_date',]

    def __str__(self):
        return f"{self.title} ({self.get_article_type_display()})"

    def get_authors_display(self):
        """Returns formatted string of authors"""
        return ", ".join([author.full_name() for author in self.authors.all().order_by('articleauthorship__authorship_order')])

    def get_citation(self, style='apa'):
        """Generates citation in specified style"""
        authors = self.get_authors_display()
        year = self.publish_date.year if self.publish_date else "n.d."
        title = self.title
        journal = f"{self.journal}" if self.journal else ""
        
        if style == 'apa':
            volume = f", {self.volume}" if self.volume else ""
            issue = f"({self.issue})" if self.issue else ""
            pages = f", {self.pages}" if self.pages else ""
            doi = f", https://doi.org/{self.doi}" if self.doi else ""
            return f"{authors} ({year}). {title}. {journal}{volume}{issue}{pages}{doi}"
        elif style == 'mla':
            return f"{authors}. \"{title}.\" {journal}, {year}{', pp. ' + self.pages if self.pages else ''}."
        else:  # Default to APA
            return self.get_citation(style='apa')

    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')
    
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def create_from_template(self, template_id):
        """Create article sections from a template"""
        template = ArticleTemplate.objects.get(id=template_id)
        self.template = template
        self.save()
        
        for section in template.sections.all().order_by('default_position'):
            ArticleSection.objects.create(
                article=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position,
                guidance=section.description
            )

class ArticleAuthorship(models.Model):
    """
    Enhanced through model for Article-Author relationship
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
    email = models.EmailField(
        blank=True,
        verbose_name='Author Email for this work'
    )

    class Meta:
        verbose_name = 'Article Authorship'
        verbose_name_plural = 'Article Authorships'
        ordering = ['authorship_order']
        unique_together = ('article', 'author')

    def __str__(self):
        return f"{self.author.full_name()} in {self.article.title}"

@reversion.register()
class ArticleSection(models.Model):
    """
    Enhanced model for article sections with versioning
    """
    SECTION_TYPES = (
        # Common sections
        ('abstract', 'Abstract'),
        ('introduction', 'Introduction'),
        
        # Research Method sections
        ('method', 'Method'),
        ('stimuli', 'Stimuli'),
        ('subject', 'Subject'),
        ('procedure', 'Procedure'),
        ('data_acquisition', 'Data acquisition and analysis'),
        ('equipment', 'Equipment'),
        
        # Research sections
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
    guidance = models.TextField(
        blank=True,
        verbose_name='Writing Guidance'
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Word Count'
    )
    
    class Meta:
        verbose_name = 'Article Section'
        verbose_name_plural = 'Article Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.article.title}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(re.sub(r'<[^>]+>', '', self.content).split())
        super().save(*args, **kwargs)

class ArticleTemplate(models.Model):
    """
    Enhanced template model for articles
    """
    ARTICLE_TYPES = Article.ARTICLE_TYPES
    
    name = models.CharField(max_length=100, verbose_name='Template Name')
    article_type = models.CharField(
        max_length=100,
        choices=ARTICLE_TYPES,
        verbose_name='Article Type'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    discipline = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Discipline'
    )
    journal = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Target Journal'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Default Template'
    )
    
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

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other default for this article type
            ArticleTemplate.objects.filter(
                article_type=self.article_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class ArticleTemplateSection(models.Model):
    """
    Enhanced template section model
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
    word_count_guide = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Word Count Guide'
    )
    example = models.TextField(
        blank=True,
        verbose_name='Example Content'
    )
    
    class Meta:
        verbose_name = 'Template Section'
        verbose_name_plural = 'Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"



# ## Research Project Models ##
@reversion.register()
class ResearchProject(models.Model):
    """
    Enhanced Research Project model
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='researchproject', verbose_name='Project' )
    # Research project metadata
    title = models.CharField(max_length=500, verbose_name='Title')
    organization = models.CharField(max_length=200, verbose_name='Organization')
    research_code = models.CharField(max_length=50, verbose_name='Research Code', blank=True)
    supervisor=models.CharField(max_length=50, verbose_name='Supervisor', blank=True)
    
    research_team = models.ManyToManyField(
        Author,
        related_name='team_projects',
        blank=True,
        verbose_name='Research Team'
    )
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total Budget'
    )
    funding_source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Funding Source'
    )
    grant_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Grant Number'
    )
    
    # Research outputs
    publications = models.ManyToManyField(
        Article,
        blank=True,
        verbose_name='Related Publications'
    )
    deliverables = models.TextField(
        blank=True,
        verbose_name='Project Deliverables'
    )
    research_project_status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
        ),
        default='draft',
        verbose_name='Status'
    )
    
    # Template reference
    template = models.ForeignKey(
        'ResearchProjectTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Project Template'
    )
    references = GenericRelation('Reference', content_type_field='cited_content_type', object_id_field='cited_object_id', related_query_name='researchproject')

    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    @property
    def owner(self):
        """دسترسی به مالک از طریق پروژه مرتبط"""
        return self.project.owner if self.project else None

    def create_from_template(self, template_id):
        """Create project sections from a template"""
        template = ResearchProjectTemplate.objects.get(id=template_id)
        self.template = template
        self.save()
        
        for section in template.sections.all().order_by('default_position'):
            ResearchProjectSection.objects.create(
                research_project=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position,
                guidance=section.description
            )

    class Meta:
        verbose_name = 'Research Project'
        verbose_name_plural = 'Research Projects'

    def __str__(self):
        return f"Research Project: {self.project.title}"

@reversion.register()
class ResearchProjectSection(models.Model):
    """
    Enhanced Research Project Section model
    """
    SECTION_TYPES = (
        ('subject', 'Subject'),
        ('stimuli', 'Stimuli'),
        ('equipment', 'Equipment'),
        ('materials', 'Materials/Instruments'),
        ('procedure', 'Procedure'),
        ('data_acquisition', 'Data acquisition and analysis'),
        ('ethical_considerations', 'Ethical Considerations'),
    )
    
    research_project = models.ForeignKey(
        ResearchProject,
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
    guidance = models.TextField(
        blank=True,
        verbose_name='Writing Guidance'
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Word Count'
    )
    
    class Meta:
        verbose_name = 'Research Project Section'
        verbose_name_plural = 'Research Project Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.research_project}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(re.sub(r'<[^>]+>', '', self.content).split())
        super().save(*args, **kwargs)

class ResearchProjectTemplate(models.Model):
    """
    Research Project Template model
    """
    name = models.CharField(max_length=100, verbose_name='Template Name')
    description = models.TextField(blank=True, verbose_name='Description')
    disciplines = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Applicable Disciplines'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Default Template'
    )
    
    sections = models.ManyToManyField(
        'ResearchProjectTemplateSection',
        related_name='templates',
        verbose_name='Sections'
    )
    
    class Meta:
        verbose_name = 'Research Project Template'
        verbose_name_plural = 'Research Project Templates'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other default templates
            ResearchProjectTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class ResearchProjectTemplateSection(models.Model):
    """
    Research Project Template Section model
    """
    SECTION_TYPES = ResearchProjectSection.SECTION_TYPES
    
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
    example = models.TextField(
        blank=True,
        verbose_name='Example Content'
    )
    
    class Meta:
        verbose_name = 'Project Template Section'
        verbose_name_plural = 'Project Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"



## Book Models ##

@reversion.register()
class Book(models.Model):
    """
    Enhanced Book model with comprehensive publishing fields
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='books', verbose_name='Project' )
    # Book metadata
    title = models.CharField(max_length=500, verbose_name='Title')
    publisher = models.CharField(max_length=200, verbose_name='Publisher')
    publish_date = models.DateField(verbose_name='Publish Date', null=True, blank=True)
    isbn = models.CharField(max_length=100, verbose_name='ISBN', blank=True)
    isbn_13 = models.CharField(max_length=100, verbose_name='ISBN-13', blank=True)
    page_count = models.PositiveIntegerField(verbose_name='Page Count', null=True, blank=True)
    authors = models.ManyToManyField(
        Author,
        through='BookAuthorship',
        verbose_name='Authors'
    )
    edition = models.PositiveIntegerField(verbose_name='Edition', default=1)
    is_published = models.BooleanField(default=False, verbose_name='Published')
    cover_image = models.ImageField(
        upload_to='book_covers/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Cover Image'
    )
    
    # Book structure fields
    preface = HTMLField(verbose_name='Preface', blank=True)
    introduction = HTMLField(verbose_name='Introduction', blank=True)
    conclusion = HTMLField(verbose_name='Conclusion', blank=True)
    bibliography = HTMLField(verbose_name='Bibliography', blank=True)
    index = HTMLField(verbose_name='Index', blank=True)
    
    # Royalty and rights
    royalty_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Royalty Percentage'
    )
    copyright_holder = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Copyright Holder'
    )
    copyright_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Copyright Year'
    )
    references = GenericRelation('Reference', content_type_field='cited_content_type', object_id_field='cited_object_id', related_query_name='book')
    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"Book: {self.title}"

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def total_chapters(self):
        """Returns total number of chapters"""
        return self.chapters.count()

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.slug})

class BookAuthorship(models.Model):
    """
    Enhanced through model for Book-Author relationship
    """
    ROLES = (
        ('author', 'Author'),
        ('editor', 'Editor'),
        ('translator', 'Translator'),
        ('contributor', 'Contributor'),
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name='Book'
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='author',
        verbose_name='Role'
    )
    chapter = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Chapters Contributed'
    )
    royalty_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Royalty Share Percentage'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order in Listing'
    )

    class Meta:
        verbose_name = 'Book Authorship'
        verbose_name_plural = 'Book Authorships'
        ordering = ['order']
        unique_together = ('book', 'author', 'role')

    def __str__(self):
        return f"{self.author.full_name()} ({self.get_role_display()}) in {self.book.title}"

@reversion.register()
class BookChapter(models.Model):
    """
    Enhanced Book Chapter model with versioning
    """
    book = models.ForeignKey(
        Book,
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
    word_count = models.PositiveIntegerField(default=0, verbose_name='Word Count')
    book_status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('published', 'Published'),
        ),
        default='draft',
        verbose_name='Status'
    )
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
        book_title = self.book.title if self.book else self.translated_book.title
        return f"Chapter {self.chapter_number}: {self.title} ({book_title})"

    def save(self, *args, **kwargs):
        # Calculate word count from sections
        if self.sections.exists():
            self.word_count = sum(section.word_count for section in self.sections.all())
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chapter_detail', kwargs={'pk': self.pk})

@reversion.register()
class BookSection(models.Model):
    """
    Enhanced Book Section model with versioning
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
        ('sidebar', 'Sidebar'),
        ('example', 'Example'),
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
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Word Count'
    )
    
    class Meta:
        verbose_name = 'Book Section'
        verbose_name_plural = 'Book Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.chapter.title}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(re.sub(r'<[^>]+>', '', self.content).split())
        super().save(*args, **kwargs)
        
        # Update chapter word count
        self.chapter.save()

@reversion.register()
class BookFigure(models.Model):
    """
    Enhanced Book Figure model with versioning
    """
    chapter = models.ForeignKey(
        BookChapter,
        on_delete=models.CASCADE,
        related_name='figures',
        verbose_name='Chapter'
    )
    figure_number = models.PositiveIntegerField(verbose_name='Figure Number')
    title = models.CharField(max_length=200, verbose_name='Figure Title')
    description = models.TextField(blank=True, verbose_name='Description')
    image = models.ImageField(
        upload_to='book_figures/%Y/%m/%d/',
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
    caption = models.TextField(
        blank=True,
        verbose_name='Caption'
    )
    license = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='License'
    )

    class Meta:
        verbose_name = 'Book Figure'
        verbose_name_plural = 'Book Figures'
        ordering = ['position']

    def __str__(self):
        return f"Figure {self.figure_number}: {self.title} ({self.chapter.title})"

    def save(self, *args, **kwargs):
        if not self.figure_number:
            # Auto-assign figure number
            last_figure = BookFigure.objects.filter(chapter=self.chapter).order_by('-figure_number').first()
            self.figure_number = last_figure.figure_number + 1 if last_figure else 1
        super().save(*args, **kwargs)

@reversion.register()
class BookTable(models.Model):
    """
    Enhanced Book Table model with versioning
    """
    chapter = models.ForeignKey(
        BookChapter,
        on_delete=models.CASCADE,
        related_name='tables',
        verbose_name='Chapter'
    )
    table_number = models.PositiveIntegerField(verbose_name='Table Number')
    title = models.CharField(max_length=200, verbose_name='Table Title')
    content = HTMLField(verbose_name='Table Content', blank=True)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name='Position in Chapter'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    source = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Source'
    )
    caption = models.TextField(
        blank=True,
        verbose_name='Caption'
    )

    class Meta:
        verbose_name = 'Book Table'
        verbose_name_plural = 'Book Tables'
        ordering = ['position']

    def __str__(self):
        return f"Table {self.table_number}: {self.title} ({self.chapter.title})"

    def save(self, *args, **kwargs):
        if not self.table_number:
            # Auto-assign table number
            last_table = BookTable.objects.filter(chapter=self.chapter).order_by('-table_number').first()
            self.table_number = last_table.table_number + 1 if last_table else 1
        super().save(*args, **kwargs)

@reversion.register()
class TranslatedBook(models.Model):
    """
    Enhanced Translated Book model
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='translatebooks', verbose_name='Project' )
    # Translation metadata
    title = models.CharField(max_length=500, verbose_name='Title')
    original_title = models.CharField(max_length=200, verbose_name='Original Title')
    original_language = models.CharField(max_length=100, verbose_name='Original Language')
    publisher = models.CharField(max_length=200, verbose_name='Publisher')
    publish_date = models.DateField(verbose_name='Publish Date', null=True, blank=True)
    isbn = models.CharField(max_length=100, verbose_name='ISBN', blank=True)
    isbn_13 = models.CharField(max_length=100, verbose_name='ISBN-13', blank=True)
    page_count = models.PositiveIntegerField(verbose_name='Page Count', null=True, blank=True)
    translator = models.ManyToManyField(
        Author,
        through='TranslationAuthorship',
        verbose_name='Translators'
    )
    original_author = models.CharField(max_length=200, verbose_name='Original Author')
    is_published = models.BooleanField(default=False, verbose_name='Published')
    cover_image = models.ImageField(
        upload_to='translated_book_covers/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Cover Image'
    )
    
    # Translation structure fields
    translator_preface = HTMLField(verbose_name='Translator Preface', blank=True)
    original_preface = HTMLField(verbose_name='Original Preface', blank=True)
    introduction = HTMLField(verbose_name='Introduction', blank=True)
    conclusion = HTMLField(verbose_name='Conclusion', blank=True)
    bibliography = HTMLField(verbose_name='Bibliography', blank=True)
    index = HTMLField(verbose_name='Index', blank=True)
    
    # Rights and permissions
    translation_rights_holder = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Translation Rights Holder'
    )
    translation_rights_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Translation Rights Year'
    )
    royalty_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Royalty Percentage'
    )

    class Meta:
        verbose_name = 'Translated Book'
        verbose_name_plural = 'Translated Books'

    def __str__(self):
        return f"Translated Book: {self.title}"

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def total_chapters(self):
        """Returns total number of chapters"""
        return self.chapters.count()

class TranslationAuthorship(models.Model):
    """
    Through model for TranslatedBook-Translator relationship
    """
    ROLES = (
        ('translator', 'Translator'),
        ('editor', 'Editor'),
        ('proofreader', 'Proofreader'),
    )
    
    book = models.ForeignKey(
        TranslatedBook,
        on_delete=models.CASCADE,
        verbose_name='Book'
    )
    translator = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name='Translator'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='translator',
        verbose_name='Role'
    )
    chapters = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Chapters Translated'
    )
    royalty_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name='Royalty Share Percentage'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order in Listing'
    )

    class Meta:
        verbose_name = 'Translation Authorship'
        verbose_name_plural = 'Translation Authorships'
        ordering = ['order']
        unique_together = ('book', 'translator', 'role')

    def __str__(self):
        return f"{self.translator.full_name()} ({self.get_role_display()}) for {self.book.title}"

## Research Proposal Models ##

@reversion.register()
class ResearchProposal(models.Model):
    """
    Enhanced Research Proposal model
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='researchproposal', verbose_name='Project' )
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Title')
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
    grant_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Grant Number'
    )
    submission_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name='Submission Deadline'
    )
    
    # Content sections
    problem_statement = HTMLField(verbose_name='Problem Statement', blank=True)
    research_importance = HTMLField(verbose_name='Research Importance', blank=True)
    literature_review = HTMLField(verbose_name='Literature Review', blank=True)
    research_objectives = HTMLField(verbose_name='Research Objectives', blank=True)
    research_methodology = HTMLField(verbose_name='Research Methodology', blank=True)
    expected_results = HTMLField(verbose_name='Expected Results', blank=True)
    
    # Team information
    principal_investigator = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_proposals',
        verbose_name='Principal Investigator'
    )
    co_investigators = models.ManyToManyField(
        Author,
        related_name='collaborated_proposals',
        blank=True,
        verbose_name='Co-Investigators'
    )
    
    # Status
    submission_status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('funded', 'Funded'),
        ),
        default='draft',
        verbose_name='Status'
    )
    
    # Template reference
    template = models.ForeignKey(
        'ResearchProposalTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Proposal Template'
    )
    references = GenericRelation('Reference', content_type_field='cited_content_type', object_id_field='cited_object_id', related_query_name='researchproposal')

    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    def create_from_template(self, template_id):
        """Create proposal sections from a template"""
        template = ResearchProposalTemplate.objects.get(id=template_id)
        self.template = template
        self.save()
        
        for section in template.sections.all().order_by('default_position'):
            ResearchProposalSection.objects.create(
                proposal=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position,
                guidance=section.description
            )

    class Meta:
        verbose_name = 'Research Proposal'
        verbose_name_plural = 'Research Proposals'

    def __str__(self):
        return f"Research Proposal: {self.title}"

@reversion.register()
class ResearchProposalSection(models.Model):
    """
    Enhanced Research Proposal Section model
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
        ('appendices', 'Appendices'),
        ('team', 'Research Team'),
        ('facilities', 'Facilities and Resources'),
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
    guidance = models.TextField(
        blank=True,
        verbose_name='Writing Guidance'
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Word Count'
    )
    
    class Meta:
        verbose_name = 'Research Proposal Section'
        verbose_name_plural = 'Research Proposal Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.proposal.title}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(re.sub(r'<[^>]+>', '', self.content).split())
        super().save(*args, **kwargs)

class ResearchProposalTemplate(models.Model):
    """
    Enhanced Research Proposal Template model
    """
    name = models.CharField(max_length=100, verbose_name='Template Name')
    description = models.TextField(blank=True, verbose_name='Description')
    disciplines = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Applicable Disciplines'
    )
    funding_agency = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Funding Agency'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Default Template'
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

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other default templates
            ResearchProposalTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class ResearchProposalTemplateSection(models.Model):
    """
    Enhanced Research Proposal Template Section model
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
    word_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Word Limit'
    )
    example = models.TextField(
        blank=True,
        verbose_name='Example Content'
    )
    
    class Meta:
        verbose_name = 'Proposal Template Section'
        verbose_name_plural = 'Proposal Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"


@reversion.register()
class Thesis(models.Model):
    """
    Enhanced Thesis model with comprehensive academic fields
    """
    project = models.ForeignKey( Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='thesis', verbose_name='Project' )
    title = models.CharField(max_length=500, verbose_name='Title')
    DEGREE_TYPES = (
        ('bachelor', "Bachelor's Thesis"),
        ('master', "Master's Thesis"),
        ('phd', 'PhD Dissertation'),
        ('habilitation', 'Habilitation Thesis'),
    )
    
    # Thesis metadata
    student_name = models.CharField(max_length=100, verbose_name='Student Name')
    student_id = models.CharField(max_length=50, blank=True, verbose_name='Student ID')
    university = models.CharField(max_length=200, verbose_name='University')
    department = models.CharField(max_length=200, blank=True, verbose_name='Department')
    faculty = models.CharField(max_length=200, blank=True, verbose_name='Faculty')
    degree_type = models.CharField(
        max_length=20,
        choices=DEGREE_TYPES,
        verbose_name='Degree Type'
    )
    defense_date = models.DateField(verbose_name='Defense Date', null=True, blank=True)
    submission_date = models.DateField(verbose_name='Submission Date', null=True, blank=True)
    supervisor = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        related_name='supervised_theses',
        verbose_name='Supervisor'
    )
    advisor = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='advised_theses',
        verbose_name='Advisor'
    )
    committee = models.ManyToManyField(
        Author,
        related_name='committee_theses',
        blank=True,
        verbose_name='Committee Members'
    )
    grade = models.CharField(max_length=50, verbose_name='Grade', blank=True)
    thesis_file = models.FileField(
        upload_to='theses/%Y/%m/%d/',
        verbose_name='Thesis File',
        null=True,
        blank=True
    )
    keywords = models.ManyToManyField(Keyword, blank=True, verbose_name='Keywords', related_name='theses')
    
    # Template reference
    template = models.ForeignKey(
        'ThesisTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Thesis Template'
    )
    references = GenericRelation('Reference', content_type_field='cited_content_type', object_id_field='cited_object_id', related_query_name='thesis')
    def get_sections(self):
        """Returns all sections ordered by their position"""
        return self.sections.all().order_by('position')

    def get_chapters(self):
        """Returns all chapters ordered by their number"""
        return self.chapters.all().order_by('chapter_number')

    def create_from_template(self, template_id):
        """Create thesis sections from a template"""
        template = ThesisTemplate.objects.get(id=template_id)
        self.template = template
        self.save()
        
        for section in template.sections.all().order_by('default_position'):
            ThesisSection.objects.create(
                thesis=self,
                section_type=section.section_type,
                title=section.title,
                position=section.default_position,
                guidance=section.description
            )

    class Meta:
        verbose_name = 'Thesis'
        verbose_name_plural = 'Theses'

    def __str__(self):
        return f"Thesis: {self.title}"

@reversion.register()
class ThesisSection(models.Model):
    """
    Enhanced Thesis Section model
    """
    SECTION_TYPES = (
        ('approval', 'Approval Page'),
        ('dedication', 'Dedication'),
        ('acknowledgments', 'Acknowledgments'),
        ('abstract', 'Abstract'),
        ('table_of_contents', 'Table of Contents'),
        ('list_of_tables', 'List of Tables'),
        ('list_of_figures', 'List of Figures'),
        ('list_of_abbreviations', 'List of Abbreviations'),
        ('list_of_symbols', 'List of Symbols'),
        ('introduction', 'Introduction'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology'),
        ('results', 'Results'),
        ('discussion', 'Discussion'),
        ('conclusion', 'Conclusion'),
        ('recommendations', 'Recommendations'),
        ('appendices', 'Appendices'),
        ('cv', 'Curriculum Vitae'),
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
    guidance = models.TextField(
        blank=True,
        verbose_name='Writing Guidance'
    )
    word_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Word Count'
    )
    
    class Meta:
        verbose_name = 'Thesis Section'
        verbose_name_plural = 'Thesis Sections'
        ordering = ['position']

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.thesis.title}"

    def save(self, *args, **kwargs):
        # Calculate word count
        if self.content:
            self.word_count = len(re.sub(r'<[^>]+>', '', self.content).split())
        super().save(*args, **kwargs)

@reversion.register()
class ThesisChapter(models.Model):
    """
    Enhanced Thesis Chapter model
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
    word_count = models.PositiveIntegerField(default=0, verbose_name='Word Count')
    thesis_status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('approved', 'Approved'),
        ),
        default='draft',
        verbose_name='Status'
    )
    
    class Meta:
        verbose_name = 'Thesis Chapter'
        verbose_name_plural = 'Thesis Chapters'
        ordering = ['chapter_number']

    def __str__(self):
        return f"Chapter {self.chapter_number}: {self.title}"

    def save(self, *args, **kwargs):
        # Calculate word count from sections
        if self.sections.exists():
            self.word_count = sum(section.word_count for section in self.sections.all())
        super().save(*args, **kwargs)

class ThesisTemplate(models.Model):
    """
    Enhanced Thesis Template model
    """
    name = models.CharField(max_length=100, verbose_name='Template Name')
    description = models.TextField(blank=True, verbose_name='Description')
    university = models.CharField(max_length=200, verbose_name='University')
    department = models.CharField(max_length=200, blank=True, verbose_name='Department')
    faculty = models.CharField(max_length=200, blank=True, verbose_name='Faculty')
    degree_type = models.CharField(
        max_length=20,
        choices=Thesis.DEGREE_TYPES,
        verbose_name='Degree Type'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='Default Template'
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

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other default for this degree type
            ThesisTemplate.objects.filter(
                degree_type=self.degree_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

class ThesisTemplateSection(models.Model):
    """
    Enhanced Thesis Template Section model
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
    word_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Word Limit'
    )
    example = models.TextField(
        blank=True,
        verbose_name='Example Content'
    )
    
    class Meta:
        verbose_name = 'Thesis Template Section'
        verbose_name_plural = 'Thesis Template Sections'
        ordering = ['default_position']
        
    def __str__(self):
        return f"{self.get_section_type_display()} (Required: {self.required})"



# Notification Models ##

class Notification(models.Model):
    """
    Notification system for user activities
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=50,
        choices=(
            ('project_update', 'Project Update'),
            ('collaboration', 'Collaboration'),
            ('comment', 'Comment'),
            ('mention', 'Mention'),
            ('system', 'System'),
        )
    )
    related_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('related_content_type', 'related_object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."

## Webhook Models ##

class Webhook(models.Model):
    """
    Webhook system for integrations
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    name = models.CharField(max_length=100)
    target_url = models.URLField()
    event_types = models.CharField(max_length=255)  # Comma-separated event types
    secret = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Webhook: {self.name} ({self.target_url})"

 ## Reference Models ##
class Reference(models.Model):
    type=( ('article', 'مقاله'), ('book', 'کتاب'), ('thesis', 'پایان‌نامه'), )
    cited_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='cited_references',limit_choices_to={'model__in': [m[0] for m in type]},default='article')
    cited_object_id = models.PositiveIntegerField()
    cited_object = GenericForeignKey('cited_content_type', 'cited_object_id')
    citing_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='citing_references')
    citing_object_id = models.PositiveIntegerField()
    citing_object = GenericForeignKey('citing_content_type', 'citing_object_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    