from django.contrib import admin
from Main.models import *
from tinymce.widgets import TinyMCE
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models

# Inline Classes
class ArticleInline(admin.StackedInline):
    model = Article
    extra = 0

class ResearchProjectInline(admin.StackedInline):
    model = ResearchProject
    extra = 0

class BookInline(admin.StackedInline):
    model = Book
    extra = 0

class TranslatedBookInline(admin.StackedInline):
    model = TranslatedBook
    extra = 0

class ResearchProposalInline(admin.StackedInline):
    model = ResearchProposal
    extra = 0

class ThesisInline(admin.StackedInline):
    model = Thesis
    extra = 0

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0

class ProjectCommentInline(admin.TabularInline):
    model = ProjectComment
    extra = 0

class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class ArticleTemplateSectionInline(admin.TabularInline):
    model = ArticleTemplate.sections.through
    extra = 0

class ResearchProjectTemplateSectionInline(admin.TabularInline):
    model = ResearchProjectTemplate.sections.through
    extra = 0

class ResearchProposalTemplateSectionInline(admin.TabularInline):
    model = ResearchProposalTemplate.sections.through
    extra = 0

class ThesisTemplateSectionInline(admin.TabularInline):
    model = ThesisTemplate.sections.through
    extra = 0

class ArticleAuthorshipInline(admin.TabularInline):
    model = ArticleAuthorship
    extra = 1
    fields = ('author', 'is_corresponding', 'authorship_order', 'affiliation')

class ResearchProjectSectionInline(admin.StackedInline):
    model = ResearchProjectSection
    extra = 0

class BookAuthorshipInline(admin.TabularInline):
    model = BookAuthorship
    extra = 1
    fields = ('author', 'role', 'chapter', 'royalty_share', 'order')

class BookChapterInline(admin.StackedInline):
    model = BookChapter
    extra = 0

class BookSectionInline(admin.StackedInline):
    model = BookSection
    extra = 0

class BookFigureInline(admin.StackedInline):
    model = BookFigure
    extra = 0

class BookTableInline(admin.StackedInline):
    model = BookTable
    extra = 0

class TranslationAuthorshipInline(admin.TabularInline):
    model = TranslationAuthorship
    extra = 1
    fields = ('translator', 'role', 'chapters', 'royalty_share', 'order')

class ResearchProposalSectionInline(admin.StackedInline):
    model = ResearchProposalSection
    extra = 0

class ThesisSectionInline(admin.StackedInline):
    model = ThesisSection
    extra = 0

class ThesisChapterInline(admin.StackedInline):
    model = ThesisChapter
    extra = 0


class ReferenceInline(GenericTabularInline):
    model = Reference
    extra = 0
    ct_field = 'cited_content_type'  # This should match your model's content_type field name
    ct_fk_field = 'cited_object_id'  # This should match your model's object_id field name
    fields = ('cited_content_type', 'cited_object_id', 'citing_content_type', 'citing_object_id', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'Reference'
    verbose_name_plural = 'References'

# Admin Classes
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'academic_degree', 'university', 'email_confirmed')
    search_fields = ('user__username', 'academic_degree', 'university')
    list_filter = ('email_confirmed', 'created_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'bio', 'phone_number', 'birth_date')
        }),
        ('Academic Information', {
            'fields': ('academic_degree', 'field_of_study', 'university', 'department', 'position')
        }),
        ('Social Profiles', {
            'fields': ('website', 'linkedin', 'google_scholar', 'researchgate'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('email_confirmed', 'public_profile')
        }),
    )

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('term', 'slug')
    search_fields = ('term', 'slug')
    prepopulated_fields = {'slug': ('term',)}
    ordering = ('term',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'orcid_id', 'affiliation', 'user')
    search_fields = ('last_name', 'first_name', 'orcid_id', 'affiliation', 'user__username')
    list_filter = ('affiliation',)
    ordering = ('last_name', 'first_name')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'user')
        }),
        ('Academic Information', {
            'fields': ('affiliation', 'department', 'orcid_id')
        }),
        ('Research Profiles', {
            'fields': ('researcher_id', 'scopus_id', 'google_scholar_id'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'progress', 'visibility', 'owner', 'created_at')
    list_filter = ('type', 'status', 'visibility', 'created_at')
    search_fields = ('title', 'owner__username', 'description')
    list_editable = ('status', 'progress')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        ArticleInline, 
        ResearchProjectInline,
        BookInline,
        TranslatedBookInline,
        ResearchProposalInline,
        ThesisInline,
        TaskInline, 
        ProjectCommentInline,
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'type', 'owner')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress', 'visibility')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Collaboration', {
            'fields': ('collaborators', 'related_projects'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_type', 'journal', 'is_published', 'citation_count', 'aricale_status')
    list_filter = ('article_type', 'is_published', 'aricale_status')
    search_fields = ('title', 'journal', 'doi', 'keywords__term')
    list_editable = ('is_published',)
    inlines = [ArticleSectionInline, ArticleAuthorshipInline, ReferenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'article_type', 'subtitle', 'keywords')
        }),
        ('Publication Details', {
            'fields': ('journal', 'volume', 'issue', 'pages', 'doi', 'is_published', 'publish_date')
        }),
        ('Status', {
            'fields': ('aricale_status', 'submitted_date', 'accepted_date'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('citation_count', 'download_count', 'view_count'),
            'classes': ('collapse',)
        }),
        ('Files', {
            'fields': ('manuscript', 'supplementary_materials'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ArticleSection)
class ArticleSectionAdmin(admin.ModelAdmin):
    list_display = ('article', 'section_type', 'title', 'position', 'word_count')
    list_filter = ('section_type',)
    search_fields = ('article__title', 'title', 'content')
    ordering = ('article', 'position')
    list_select_related = ('article',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(ArticleTemplate)
class ArticleTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_type', 'discipline', 'journal', 'is_default')
    list_filter = ('article_type', 'is_default')
    search_fields = ('name', 'description', 'discipline', 'journal')
    exclude = ('sections',)
    inlines = [ArticleTemplateSectionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'article_type', 'description', 'is_default')
        }),
        ('Target Information', {
            'fields': ('discipline', 'journal'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ArticleTemplateSection)
class ArticleTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position', 'word_count_guide')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description', 'example')
    ordering = ('default_position',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('section_type', 'title', 'required', 'default_position')
        }),
        ('Guidance', {
            'fields': ('description', 'word_count_guide', 'example'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'organization', 'supervisor', 'research_project_status')
    list_filter = ('research_project_status', 'organization')
    search_fields = ('project__title', 'title', 'organization', 'supervisor', 'research_code')
    inlines = [ResearchProjectSectionInline, ReferenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'organization', 'research_code', 'supervisor', 'template')
        }),
        ('Funding', {
            'fields': ('budget', 'funding_source', 'grant_number')
        }),
        ('Team & Outputs', {
            'fields': ('research_team', 'publications', 'deliverables'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('research_project_status',)
        }),
    )

@admin.register(ResearchProjectSection)
class ResearchProjectSectionAdmin(admin.ModelAdmin):
    list_display = ('research_project', 'section_type', 'title', 'position', 'word_count')
    list_filter = ('section_type',)
    search_fields = ('research_project__title', 'title', 'content')
    ordering = ('research_project', 'position')
    list_select_related = ('research_project',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'is_published', 'edition', 'copyright_year')
    list_filter = ('is_published', 'edition')
    search_fields = ('title', 'publisher', 'isbn', 'isbn_13')
    inlines = [BookAuthorshipInline, BookChapterInline, ReferenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'publisher', 'is_published')
        }),
        ('Publication Details', {
            'fields': ('publish_date', 'isbn', 'isbn_13', 'page_count', 'edition')
        }),
        ('Content', {
            'fields': ('preface', 'introduction', 'conclusion', 'bibliography', 'index'),
            'classes': ('collapse',)
        }),
        ('Rights & Royalties', {
            'fields': ('copyright_holder', 'copyright_year', 'royalty_percentage'),
            'classes': ('collapse',)
        }),
        ('Cover Image', {
            'fields': ('cover_image',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookChapter)
class BookChapterAdmin(admin.ModelAdmin):
    list_display = ('book', 'chapter_number', 'title', 'word_count', 'book_status')
    list_filter = ('book_status',)
    search_fields = ('book__title', 'title', 'summary')
    ordering = ('book', 'chapter_number')
    list_select_related = ('book',)
    inlines = [BookSectionInline, BookFigureInline, BookTableInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('book', 'chapter_number', 'title', 'book_status')
        }),
        ('Content', {
            'fields': ('summary', 'word_count'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookSection)
class BookSectionAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'section_type', 'title', 'position', 'word_count')
    list_filter = ('section_type',)
    search_fields = ('chapter__title', 'title', 'content')
    ordering = ('chapter', 'position')
    list_select_related = ('chapter',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(BookFigure)
class BookFigureAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'figure_number', 'title', 'position')
    search_fields = ('chapter__title', 'title', 'description', 'caption')
    ordering = ('chapter', 'figure_number')
    list_select_related = ('chapter',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('chapter', 'figure_number', 'title', 'position')
        }),
        ('Content', {
            'fields': ('description', 'image', 'caption'),
            'classes': ('collapse',)
        }),
        ('Source & Rights', {
            'fields': ('source', 'license'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookTable)
class BookTableAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'table_number', 'title', 'position')
    search_fields = ('chapter__title', 'title', 'content', 'caption')
    ordering = ('chapter', 'table_number')
    list_select_related = ('chapter',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    fieldsets = (
        ('Basic Information', {
            'fields': ('chapter', 'table_number', 'title', 'position')
        }),
        ('Content', {
            'fields': ('content', 'caption'),
            'classes': ('collapse',)
        }),
        ('Source & Notes', {
            'fields': ('source', 'notes'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TranslatedBook)
class TranslatedBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_title', 'original_language', 'publisher', 'is_published')
    list_filter = ('original_language', 'is_published')
    search_fields = ('title', 'original_title', 'publisher', 'isbn', 'isbn_13')
    inlines = [TranslationAuthorshipInline, BookChapterInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'original_title', 'original_language', 'publisher', 'is_published')
        }),
        ('Publication Details', {
            'fields': ('publish_date', 'isbn', 'isbn_13', 'page_count')
        }),
        ('Content', {
            'fields': ('translator_preface', 'original_preface', 'introduction', 'conclusion', 'bibliography', 'index'),
            'classes': ('collapse',)
        }),
        ('Rights & Royalties', {
            'fields': ('translation_rights_holder', 'translation_rights_year', 'royalty_percentage'),
            'classes': ('collapse',)
        }),
        ('Cover Image', {
            'fields': ('cover_image',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ResearchProposal)
class ResearchProposalAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'sponsor', 'budget', 'submission_status')
    list_filter = ('submission_status', 'sponsor')
    search_fields = ('project__title', 'title', 'sponsor', 'grant_number')
    inlines = [ResearchProposalSectionInline, ReferenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'template')
        }),
        ('Funding', {
            'fields': ('budget', 'duration_months', 'sponsor', 'grant_number', 'submission_deadline')
        }),
        ('Team', {
            'fields': ('principal_investigator', 'co_investigators'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('problem_statement', 'research_importance', 'literature_review', 
                       'research_objectives', 'research_methodology', 'expected_results'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('submission_status',)
        }),
    )

@admin.register(ResearchProposalSection)
class ResearchProposalSectionAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'section_type', 'title', 'position', 'word_count')
    list_filter = ('section_type',)
    search_fields = ('proposal__title', 'title', 'content')
    ordering = ('proposal', 'position')
    list_select_related = ('proposal',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'student_name', 'degree_type', 'university', 'defense_date')
    list_filter = ('degree_type', 'university')
    search_fields = ('project__title', 'title', 'student_name', 'student_id', 'supervisor__last_name')
    inlines = [ThesisSectionInline, ThesisChapterInline, ReferenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'template')
        }),
        ('Student Information', {
            'fields': ('student_name', 'student_id')
        }),
        ('Academic Information', {
            'fields': ('university', 'department', 'faculty', 'degree_type')
        }),
        ('Timeline', {
            'fields': ('defense_date', 'submission_date'),
            'classes': ('collapse',)
        }),
        ('Committee', {
            'fields': ('supervisor', 'advisor', 'committee'),
            'classes': ('collapse',)
        }),
        ('Thesis Details', {
            'fields': ('keywords', 'grade'),
            'classes': ('collapse',)
        }),
        ('Files', {
            'fields': ('thesis_file',),
            'classes': ('collapse',)
        }),
    )

@admin.register(ThesisSection)
class ThesisSectionAdmin(admin.ModelAdmin):
    list_display = ('thesis', 'section_type', 'title', 'position', 'word_count')
    list_filter = ('section_type',)
    search_fields = ('thesis__title', 'title', 'content')
    ordering = ('thesis', 'position')
    list_select_related = ('thesis',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(ThesisChapter)
class ThesisChapterAdmin(admin.ModelAdmin):
    list_display = ('thesis', 'chapter_number', 'title', 'word_count', 'thesis_status')
    list_filter = ('thesis_status',)
    search_fields = ('thesis__title', 'title', 'summary')
    ordering = ('thesis', 'chapter_number')
    list_select_related = ('thesis',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('thesis', 'chapter_number', 'title', 'thesis_status')
        }),
        ('Content', {
            'fields': ('summary', 'word_count'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'due_date', 'priority', 'completed', 'assigned_to')
    list_filter = ('completed', 'priority', 'due_date')
    search_fields = ('title', 'project__title', 'assigned_to__username')
    list_editable = ('completed', 'priority')
    date_hierarchy = 'due_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description')
        }),
        ('Status', {
            'fields': ('completed', 'completed_date', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'due_date'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__title', 'author__username', 'content')
    list_select_related = ('project', 'author')
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'target_url', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'target_url', 'user__username')
    list_editable = ('is_active',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'target_url', 'is_active')
        }),
        ('Configuration', {
            'fields': ('event_types', 'secret'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('get_cited_object', 'get_citing_object', 'created_at')
    list_filter = ('cited_content_type', 'citing_content_type')
    search_fields = ('cited_object_id', 'citing_object_id')
    readonly_fields = ('created_at',)

    def get_cited_object(self, obj):
        return f"{obj.cited_content_type} (ID: {obj.cited_object_id})"
    get_cited_object.short_description = 'Cited Object'

    def get_citing_object(self, obj):
        return f"{obj.citing_content_type} (ID: {obj.citing_object_id})"
    get_citing_object.short_description = 'Citing Object'


# Template Admin Models
@admin.register(ResearchProjectTemplate)
class ResearchProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'disciplines', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name', 'description', 'disciplines')
    exclude = ('sections',)
    inlines = [ResearchProjectTemplateSectionInline]

@admin.register(ResearchProjectTemplateSection)
class ResearchProjectTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description', 'example')
    ordering = ('default_position',)

@admin.register(ResearchProposalTemplate)
class ResearchProposalTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'disciplines', 'funding_agency', 'is_default')
    list_filter = ('is_default', 'funding_agency')
    search_fields = ('name', 'description', 'disciplines')
    exclude = ('sections',)
    inlines = [ResearchProposalTemplateSectionInline]

@admin.register(ResearchProposalTemplateSection)
class ResearchProposalTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position', 'word_limit')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description', 'example')
    ordering = ('default_position',)

@admin.register(ThesisTemplate)
class ThesisTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'department', 'degree_type', 'is_default')
    list_filter = ('is_default', 'degree_type', 'university')
    search_fields = ('name', 'description', 'university', 'department')
    exclude = ('sections',)
    inlines = [ThesisTemplateSectionInline]

@admin.register(ThesisTemplateSection)
class ThesisTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position', 'word_limit')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description', 'example')
    ordering = ('default_position',)