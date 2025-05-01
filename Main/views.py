from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from Main.models import *
from Main.forms import *
from django.views.decorators.csrf import csrf_exempt
from translate import Translator
from habanero import Crossref
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
import logging
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.exceptions import PermissionDenied
import re
from datetime import datetime



# Main View
def home_page(request):
    return render(request, 'home/index.html', {})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/dashboard/')  # Redirect after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    return auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomAuthenticationForm,
        extra_context={
            'register_url': reverse_lazy('register'),
            'forgot_password_url': reverse_lazy('password_reset'),
        }
    )(request)

def dashboard(request):
    """
    Display the user's dashboard with categorized projects.
    """
    # Get all owned projects of the current user
    user_projects = request.user.owned_projects.all()

    # Define a dictionary to categorize projects based on their type
    project_dict = {
        'articles': [],
        'books': [],
        'translated_books': [],
        'research_proposals': [],
        'research_projects': [],
        'theses': [],
    }

    # Map project types to dictionary keys for easier categorization
    type_to_key = {
        'article_writing': 'articles',
        'book_writing': 'books',
        'book_translation': 'translated_books',
        'research_proposal': 'research_proposals',
        'research_project': 'research_projects',
        'thesis': 'theses',
    }

    # Categorize projects based on their type
    for project in user_projects:
        key = type_to_key.get(project.type)  # Get the corresponding key from the type
        if key and hasattr(project, 'researchproject') and project.researchproject.exists():
            project_dict[key].append(project.researchproject.first())
        elif key:
            project_dict[key].append(project)

    # Pass the categorized projects to the template
    return render(request, 'dashboard/dashboard.html', {
        'project_dict': project_dict,
    })

# Project View
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(owner=self.request.user) | 
            Q(collaborators=self.request.user)
        ).distinct().order_by('-created_at')
    
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project/project_create.html'
    success_url = reverse_lazy('project_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'پروژه با موفقیت ایجاد شد')
        return response

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(owner=self.request.user) | 
            Q(collaborators=self.request.user) |
            Q(visibility='public')
        ).distinct()


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project/project_form.html'
    success_url = reverse_lazy('project_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'پروژه با موفقیت به‌روزرسانی شد')
        return response

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'پروژه با موفقیت حذف شد')
        return super().delete(request, *args, **kwargs)

# Task

class TaskListView(ListView):
    model = Task
    template_name = 'task_list.html'
    context_object_name = 'tasks'

class TaskDetailView(DetailView):
    model = Task
    template_name = 'task_detail.html'

class TaskCreateView(CreateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['project', 'title', 'description', 'due_date', 'completed']
    success_url = reverse_lazy('task_list')

class TaskUpdateView(UpdateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['project', 'title', 'description', 'due_date', 'completed']
    success_url = reverse_lazy('task_list')

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

# ProjectComment Views
class ProjectCommentListView(ListView):
    model = ProjectComment
    template_name = 'comment_list.html'
    context_object_name = 'comments'

class ProjectCommentDetailView(DetailView):
    model = ProjectComment
    template_name = 'comment_detail.html'

class ProjectCommentCreateView(CreateView):
    model = ProjectComment
    template_name = 'comment_form.html'
    fields = ['project', 'author', 'content']
    success_url = reverse_lazy('comment_list')

class ProjectCommentUpdateView(UpdateView):
    model = ProjectComment
    template_name = 'comment_form.html'
    fields = ['project', 'author', 'content']
    success_url = reverse_lazy('comment_list')

class ProjectCommentDeleteView(DeleteView):
    model = ProjectComment
    template_name = 'comment_confirm_delete.html'
    success_url = reverse_lazy('comment_list')

# Article View
class ArticleListView(ListView):
    model = Article
    template_name = 'article_list.html'
    context_object_name = 'articles'

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'

class ArticleCreateView(CreateView):
    model = Article
    template_name = 'article_form.html'
    fields = ['project', 'article_type', 'title', 'doi', 'abstract', 'keywords', 'authors', 'is_published', 'publish_date']
    success_url = reverse_lazy('article_list')

class ArticleUpdateView(UpdateView):
    model = Article
    template_name = 'article_form.html'
    fields = ['project', 'article_type', 'title', 'doi', 'abstract', 'keywords', 'authors', 'is_published', 'publish_date']
    success_url = reverse_lazy('article_list')

class ArticleDeleteView(DeleteView):
    model = Article
    template_name = 'article_confirm_delete.html'
    success_url = reverse_lazy('article_list')

# Book View
# class BookListView(ListView):
#     model = Book
#     template_name = 'book_list.html'
#     context_object_name = 'books'

# class BookDetailView(DetailView):
#     model = Book
#     template_name = 'book_detail.html'

# class BookCreateView(CreateView):
#     model = Book
#     template_name = 'book_form.html'
#     fields = ['project', 'publisher', 'isbn', 'page_count', 'edition', 'preface', 'introduction', 'conclusion', 'bibliography', 'index', 'is_published']
#     success_url = reverse_lazy('book_list')

# class BookUpdateView(UpdateView):
#     model = Book
#     template_name = 'book_form.html'
#     fields = ['project', 'publisher', 'isbn', 'page_count', 'edition', 'preface', 'introduction', 'conclusion', 'bibliography', 'index', 'is_published']
#     success_url = reverse_lazy('book_list')

# class BookDeleteView(DeleteView):
#     model = Book
#     template_name = 'book_confirm_delete.html'
#     success_url = reverse_lazy('book_list')

# # TranslatedBook View
# class TranslatedBookListView(ListView):
#     model = TranslatedBook
#     template_name = 'translated_book_list.html'
#     context_object_name = 'translated_books'

# class TranslatedBookDetailView(DetailView):
#     model = TranslatedBook
#     template_name = 'translated_book_detail.html'

# class TranslatedBookCreateView(CreateView):
#     model = TranslatedBook
#     template_name = 'translated_book_form.html'
#     fields = ['project', 'original_title', 'original_language', 'translator', 'publisher', 'isbn', 'page_count', 'is_published']
#     success_url = reverse_lazy('translated_book_list')

# class TranslatedBookUpdateView(UpdateView):
#     model = TranslatedBook
#     template_name = 'translated_book_form.html'
#     fields = ['project', 'original_title', 'original_language', 'translator', 'publisher', 'isbn', 'page_count', 'is_published']
#     success_url = reverse_lazy('translated_book_list')

# class TranslatedBookDeleteView(DeleteView):
#     model = TranslatedBook
#     template_name = 'translated_book_confirm_delete.html'
#     success_url = reverse_lazy('translated_book_list')

# Research Project Views
class ResearchProjectListView(ListView):
    model = ResearchProject
    template_name = 'projects/ResearchProject/researchproject_list.html'
    context_object_name = 'research_projects'

    def get_queryset(self):
        return ResearchProject.objects.select_related('project__owner').all()
    

class ResearchProjectDetailView(DetailView):
    model = ResearchProject
    template_name = 'projects/researchproject/researchproject_detail.html'
    context_object_name = 'research_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current research project
        research_project = self.object
        
        # 1. Get citing references
        citing_references = Reference.objects.filter(
            citing_content_type=ContentType.objects.get_for_model(ResearchProject),
            citing_object_id=research_project.id
        ).select_related('cited_content_type')

        # 2. Get cited references
        cited_references = Reference.objects.filter(
            cited_content_type=ContentType.objects.get_for_model(ResearchProject),
            cited_object_id=research_project.id
        ).select_related('citing_content_type')

        # Convert to list for better display in template
        citing_refs_list = []
        for ref in citing_references:
            cited_obj = ref.cited_object
            citing_refs_list.append({
                'id': ref.id,
                'object': cited_obj,
                'type': cited_obj._meta.verbose_name,
                'created_at': ref.created_at,
                'sections': cited_obj.get_sections()  # Get sections of the cited object
            })

        cited_refs_list = []
        for ref in cited_references:
            citing_obj = ref.citing_object
            cited_refs_list.append({
                'id': ref.id,
                'object': citing_obj,
                'type': citing_obj._meta.verbose_name,
                'created_at': ref.created_at,
            })
        
        context.update({
            'sections': research_project.sections.all(),
            'citing_references': citing_refs_list,
            'cited_references': cited_refs_list,
        })
        
        return context

class ResearchProjectCreateView(LoginRequiredMixin, CreateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'projects/researchproject/researchproject_create_update.html'
    success_url = reverse_lazy('research_project_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['edit_mode'] = False
        return kwargs

    def form_valid(self, form):
        # دریافت پروژه انتخاب‌شده از فرم
        selected_project = form.cleaned_data.get('project')
        
        if not selected_project:
            # اگر پروژه‌ای انتخاب نشده باشد، خطایی نمایش دهید
            form.add_error('project', 'پروژه‌ای انتخاب نشده است.')
            return self.form_invalid(form)
        
        # طرح پژوهشی را به پروژه انتخاب‌شده متصل کنید
        form.instance.project = selected_project
        
        # ذخیره طرح پژوهشی
        response = super().form_valid(form)
        
        # اگر از قالب استفاده شود، ساختار قالب را اعمال کنید
        if form.cleaned_data.get('use_template') and form.cleaned_data.get('template'):
            self.object.create_from_template(form.cleaned_data['template'].id)
        
        # پیام موفقیت
        messages.success(self.request, 'طرح پژوهشی جدید با موفقیت ایجاد شد.')
        return response


class ResearchProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'projects/researchproject/researchproject_create_update.html'
    context_object_name = 'project'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['edit_mode'] = True
        return kwargs

    def get_success_url(self):
        return reverse('research_project_detail', kwargs={'pk': self.object.pk})

    def get_queryset(self):
        # تغییر این قسمت برای فیلتر کردن بر اساس project__owner به جای owner
        return ResearchProject.objects.filter(project__owner=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if (not self.object.template and 
            form.cleaned_data.get('use_template') and 
            form.cleaned_data.get('template')):
            self.object.create_from_template(form.cleaned_data['template'].id)
            
        messages.success(self.request, 'طرح پژوهشی با موفقیت به‌روزرسانی شد.')
        return response
    
class ResearchProjectDeleteView(DeleteView):
    model = ResearchProject
    template_name = 'projects/researchproject/pesearchproject_confirm_delete.html'
    success_url = reverse_lazy('research_project_list')

# Thesis View
# class ThesisListView(ListView):
#     model = Thesis
#     template_name = 'thesis_list.html'
#     context_object_name = 'theses'

# class ThesisDetailView(DetailView):
#     model = Thesis
#     template_name = 'thesis_detail.html'

# class ThesisCreateView(CreateView):
#     model = Thesis
#     template_name = 'thesis_form.html'
#     fields = ['project', 'student_name', 'university', 'department', 'degree_type', 'defense_date']
#     success_url = reverse_lazy('thesis_list')

# class ThesisUpdateView(UpdateView):
#     model = Thesis
#     template_name = 'thesis_form.html'
#     fields = ['project', 'student_name', 'university', 'department', 'degree_type', 'defense_date']
#     success_url = reverse_lazy('thesis_list')

# class ThesisDeleteView(DeleteView):
#     model = Thesis
#     template_name = 'thesis_confirm_delete.html'
#     success_url = reverse_lazy('thesis_list')

logger = logging.getLogger(__name__)
def clean_doi(doi):
    """حذف پیشوندهای غیرضروری از DOI"""
    match = re.search(r'(10\.\d{4,9}/.+)', doi)
    if match:
        return match.group(1).strip()
    return doi.strip()

def create_article_from_doi(doi):
    """ایجاد یا بازیابی مقاله بر اساس DOI"""
    doi = clean_doi(doi)
    
    # بررسی وجود مقاله در دیتابیس
    existing_article = Article.objects.filter(doi__iexact=doi).first()
    if existing_article:
        return existing_article

    # دریافت داده از Crossref
    cr = Crossref()
    work = cr.works(ids=doi, timeout=30)
    if not work or 'message' not in work:
        raise ValidationError("پاسخ نامعتبر از Crossref دریافت شد")
    
    data = work['message']
    
    # پردازش اطلاعات مقاله
    title = str(data.get('title', [''])[0]) or 'بدون عنوان'
    abstract = str(data.get('abstract', '')) or 'چکیده موجود نیست'
    
    # پردازش تاریخ انتشار
    pub_date = data.get('published', {}).get('date-parts', [[None]])[0]
    publish_date = None
    if pub_date and len(pub_date) >= 1:
        try:
            year = int(pub_date[0])
            publish_date = datetime(year, 1, 1).date()
        except (ValueError, TypeError):
            pass

    # ایجاد مقاله جدید
    article = Article.objects.create(
        title=title[:500],
        journal=data.get('container-title', [''])[0][:200] or '',
        volume=data.get('volume', '')[:50],
        issue=data.get('issue', '')[:50],
        pages=data.get('page', '')[:50],
        doi=doi.lower().strip(),
        publish_date=publish_date,
        aricale_status='published'
    )

    # پردازش و افزودن نویسندگان
    for order, author_data in enumerate(data.get('author', []), start=1):
        try:
            given_name = author_data.get('given', '').strip()[:100]
            family_name = author_data.get('family', '').strip()[:100]
            
            if not given_name or not family_name:
                continue

            # پردازش ORCID
            orcid = author_data.get('ORCID', '')
            if orcid:
                orcid = orcid.split('/')[-1][:19]

            # ایجاد یا بازیابی نویسنده
            author, created = Author.objects.get_or_create(
                first_name=given_name,
                last_name=family_name,
                defaults={
                    'orcid_id': orcid,
                    'affiliation': ', '.join(
                        aff.get('name', '')[:100] 
                        for aff in author_data.get('affiliation', [])
                    )[:200]
                }
            )

            # ایجاد رابطه نویسندگی
            ArticleAuthorship.objects.create(
                article=article,
                author=author,
                authorship_order=order,
                is_corresponding=order == 1
            )

        except Exception as e:
            logger.warning(f"خطا در پردازش نویسنده {order}: {str(e)}")
            continue

    return article
    

CONTENT_TYPE_MAPPING = { 'article': Article, 'book': Book, 'thesis': Thesis, 'researchproject': ResearchProject, 'researchproposal': ResearchProposal, 'translatedbook': TranslatedBook }
@require_POST
@transaction.atomic
def add_reference_with_doi(request, content_type, object_id):
    try:
        # اعتبارسنجی کاربر
        if not request.user.is_authenticated:
            raise PermissionDenied("دسترسی غیرمجاز")

        # دریافت و اعتبارسنجی DOI
        doi = request.POST.get('doi', '').strip()
        if not doi or len(doi) < 10:
            return JsonResponse(
                {'success': False, 'error': 'DOI وارد شده معتبر نیست'},
                status=400
            )

        # تشخیص مدل citing از روی content_type
        citing_model = CONTENT_TYPE_MAPPING.get(content_type.lower())
        if not citing_model:
            return JsonResponse(
                {'success': False, 'error': 'نوع محتوای درخواست شده معتبر نیست'},
                status=404
            )

        # دریافت آبجکت citing و بررسی مالکیت
        citing_obj = get_object_or_404(citing_model, id=object_id)
        
        # بررسی دسترسی کاربر
        if hasattr(citing_obj, 'owner') and citing_obj.owner != request.user:
            raise PermissionDenied("شما مجوز دسترسی به این منبع را ندارید")

        # ایجاد یا دریافت مقاله مربوط به DOI (cited object)
        try:
            cited_article = create_article_from_doi(doi)
        except Exception as e:
            logger.error(f"خطا در ایجاد مقاله از DOI {doi}: {str(e)}")
            return JsonResponse(
                {'success': False, 'error': f'خطا در پردازش DOI: {str(e)}'},
                status=400
            )

        # بررسی وجود مرجع قبلی
        existing_reference = Reference.objects.filter(
            citing_content_type=ContentType.objects.get_for_model(citing_model),
            citing_object_id=object_id,
            cited_content_type=ContentType.objects.get_for_model(Article),
            cited_object_id=cited_article.id
        ).first()

        if existing_reference:
            return JsonResponse({
                'success': False,
                'error': 'این منبع قبلاً به پروژه اضافه شده است.'
            }, status=400)

        # ایجاد رکورد مرجع
        reference = Reference.objects.create(
            citing_content_type=ContentType.objects.get_for_model(citing_model),
            citing_object_id=object_id,
            cited_content_type=ContentType.objects.get_for_model(Article),
            cited_object_id=cited_article.id,
            created_at=timezone.now()
        )

        logger.info(
            f"ارجاع جدید ایجاد شد: {content_type} {object_id} به مقاله {cited_article.id}"
        )

        return JsonResponse({
            'success': True,
            'reference_id': reference.id,
            'cited_article': {
                'id': cited_article.id,
                'title': cited_article.title,
                'authors': cited_article.get_authors_display(),
                'doi': cited_article.doi
            },
            'citing_object': {
                'type': content_type,
                'id': object_id,
                'title': str(citing_obj)
            }
        })

    except PermissionDenied as e:
        logger.warning(f"دسترسی غیرمجاز: {str(e)}")
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=403
        )
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {str(e)}", exc_info=True)
        return JsonResponse(
            {'success': False, 'error': 'خطای سرور داخلی'},
            status=500
        )

def generate_citation_key(model_type, object_id, doi):
    """
    تولید کلید استناد منحصر به فرد
    """
    doi_part = doi.replace('/', '_')[:20]
    return f"ref_{model_type[:3]}_{object_id}_{doi_part}"
    

import time
import random
from deep_translator import GoogleTranslator
def translate_text(request):
    if request.method != 'POST':
        return JsonResponse(
            {'error': 'Only POST method is allowed'},
            status=405
        )

    text = request.POST.get('text', '').strip()
    target_lang = request.POST.get('target_lang', 'fa')

    if not text:
        return JsonResponse(
            {'error': 'Text parameter is required'},
            status=400
        )

    MAX_LENGTH = 5000  # محدودیت جدید برای deep-translator
    if len(text) > MAX_LENGTH:
        return JsonResponse(
            {'error': f'Text too long (max {MAX_LENGTH} characters)'},
            status=400
        )

    def translate_chunk(chunk):
        try:
            return GoogleTranslator(
                source='auto',
                target=target_lang
            ).translate(chunk)
        except Exception as e:
            raise Exception(f'Translation failed: {str(e)}')

    try:
        # اگر متن کوتاه است مستقیماً ترجمه شود
        if len(text) <= 500:
            translation = translate_chunk(text)
            return JsonResponse({'translation': translation})
        
        # برای متن‌های طولانی:
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        translations = []
        
        for i, chunk in enumerate(chunks):
            # تاخیر تصادفی برای جلوگیری از محدودیت
            if i > 0:
                time.sleep(random.uniform(0.5, 1.5))
            
            translations.append(translate_chunk(chunk))
        
        return JsonResponse({
            'translation': ' '.join(translations),
            'chunks': len(chunks)
        })

    except Exception as e:
        return JsonResponse(
            {'error': str(e)},
            status=500
        )