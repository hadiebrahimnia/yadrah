from django.contrib import admin
from Main.models import *
from tinymce.widgets import TinyMCE
from django.contrib.contenttypes.admin import GenericTabularInline

# Inline برای مدل‌های وابسته به پروژه
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

# مدیریت پروفایل کاربر
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email_confirmed', 'created_at')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('email_confirmed', 'created_at')

# مدیریت کلمات کلیدی
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('term', 'created_at')
    search_fields = ('term',)
    ordering = ('term',)

# مدیریت پروژه‌ها
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
    filter_horizontal = ('keywords', 'related_projects', 'tags')

# مدیریت مقالات
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_type', 'publish_date', 'is_published')
    list_filter = ('article_type', 'is_published')
    search_fields = ('title', 'doi')
    inlines = [ArticleSectionInline, ArticleAuthorshipInline]
    filter_horizontal = ('keywords',)

    def get_methods_section(self, obj):
        try:
            methods_section = obj.sections.get(section_type='methodology')
            return methods_section.content[:50]  # فقط 50 کاراکتر اول
        except ArticleSection.DoesNotExist:
            return None
    
    get_methods_section.short_description = 'Research Methods'
    list_display = ['title', 'article_type', 'get_methods_section', 'is_published']

# مدیریت بخش‌های مقاله
@admin.register(ArticleSection)
class ArticleSectionAdmin(admin.ModelAdmin):
    list_display = ('article', 'section_type', 'title', 'position')
    list_filter = ('section_type',)
    search_fields = ('article__title', 'title')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

# مدیریت قالب‌های مقاله
@admin.register(ArticleTemplate)
class ArticleTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_type', 'description')
    list_filter = ('article_type',)
    search_fields = ('name', 'description')
    exclude = ('sections',)
    inlines = [ArticleTemplateSectionInline]

# مدیریت بخش‌های قالب مقاله
@admin.register(ArticleTemplateSection)
class ArticleTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title', 'required', 'default_position')
    list_filter = ('required', 'section_type')
    search_fields = ('title', 'description')

# مدیریت کتاب‌های تألیفی
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('project', 'publisher', 'edition', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('project__title', 'publisher')

# مدیریت کتاب‌های ترجمه
@admin.register(TranslatedBook)
class TranslatedBookAdmin(admin.ModelAdmin):
    list_display = ('project', 'original_title', 'original_language', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('project__title', 'original_title')

class ResearchProjectSectionInline(admin.StackedInline):
    model = ResearchProjectSection
    extra = 0

# مدیریت طرح‌های پژوهشی
@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ('project', 'organization', 'supervisor', 'research_code')
    search_fields = ('project__title', 'organization', 'supervisor')
    inlines = [ResearchProjectSectionInline]

# مدیریت پروپوزال‌های پژوهشی
@admin.register(ResearchProposal)
class ResearchProposalAdmin(admin.ModelAdmin):
    list_display = ('project', 'name_fa', 'budget', 'duration_months')
    list_filter = ('duration_months',)
    search_fields = ('project__title', 'name_fa')

# مدیریت پایان‌نامه‌ها
@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ('project', 'student_name', 'university', 'defense_date')
    list_filter = ('defense_date',)
    search_fields = ('project__title', 'student_name')

# مدیریت وظایف
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'due_date', 'completed')
    list_filter = ('completed', 'due_date')
    search_fields = ('project__title', 'title')

# مدیریت نظرات پروژه
@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('project', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('project__title', 'author__username')

# مدیریت مراجع
@admin.register(Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('authors', 'title', 'publication_date', 'reference_type')
    list_filter = ('reference_type', 'created_at')
    search_fields = ('authors', 'title', 'doi')

# مدیریت اعلان‌ها
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')

# مدیریت وب‌هُک‌ها
@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_url', 'event_types', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'target_url')