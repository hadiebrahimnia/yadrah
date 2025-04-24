from django.contrib import admin
from Main.models import *
from tinymce.widgets import TinyMCE
from django.contrib.contenttypes.admin import GenericTabularInline

class ArticleInline(admin.StackedInline):
    model = Article
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

class ResearchProjectInline(admin.StackedInline):
    model = ResearchProject
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

class ReferenceInline(GenericTabularInline):
    model = Reference
    extra = 0
    ct_field = 'content_type'
    ct_fk_field = 'object_id'

class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class ArticleTemplateSectionInline(admin.TabularInline):
    model = ArticleTemplate.sections.through
    extra = 0

class ArticleAuthorshipInline(admin.TabularInline):
    model = ArticleAuthorship
    extra = 1
    fields = ('author', 'is_corresponding', 'authorship_order', 'affiliation')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email_confirmed')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('email_confirmed', 'created_at')

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('term',)
    search_fields = ('term',)
    ordering = ('term',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'owner', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('title', 'owner__username')
    inlines = [
        ArticleInline, BookInline, TranslatedBookInline,
        ResearchProposalInline, ResearchProjectInline, ThesisInline,
        TaskInline, ProjectCommentInline, ReferenceInline
    ]

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_type', 'get_methods_section', 'is_published')
    list_filter = ('article_type', 'is_published')
    search_fields = ('title', 'doi')
    inlines = [ArticleSectionInline, ArticleAuthorshipInline]
    
    def get_methods_section(self, obj):
        try:
            methods_section = obj.sections.get(section_type='methodology')
            return methods_section.content[:50]
        except ArticleSection.DoesNotExist:
            return None
    get_methods_section.short_description = 'Research Methods'

@admin.register(ArticleSection)
class ArticleSectionAdmin(admin.ModelAdmin):
    list_display = ('article', 'section_type', 'title', 'position')
    list_filter = ('section_type',)
    search_fields = ('article__title', 'title')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(ArticleTemplate)
class ArticleTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_type', 'description')
    list_filter = ('article_type',)
    search_fields = ('name', 'description')
    exclude = ('sections',)
    inlines = [ArticleTemplateSectionInline]

@admin.register(ArticleTemplateSection)
class ArticleTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'edition', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'publisher')

@admin.register(TranslatedBook)
class TranslatedBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_title', 'original_language', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'original_title')

class ResearchProjectSectionInline(admin.StackedInline):
    model = ResearchProjectSection
    extra = 0

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'supervisor', 'research_code')
    search_fields = ('title', 'organization', 'supervisor__last_name')
    inlines = [ResearchProjectSectionInline]

@admin.register(ResearchProposal)
class ResearchProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'name_fa', 'budget', 'duration_months')
    list_filter = ('duration_months',)
    search_fields = ('title', 'name_fa')

@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_name', 'university', 'defense_date')
    list_filter = ('defense_date',)
    search_fields = ('title', 'student_name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'due_date', 'completed')
    list_filter = ('completed', 'due_date')
    search_fields = ('title', 'project__title')

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('authors', 'title', 'publication_date', 'reference_type')
    list_filter = ('reference_type',)
    search_fields = ('authors', 'title', 'doi')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_url', 'event_types', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'target_url')