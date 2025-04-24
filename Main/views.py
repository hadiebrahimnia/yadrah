from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from Main.models import *
from Main.forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from translate import Translator
from habanero import Crossref
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST

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
    user_projects = request.user.owned_projects.all()  # Get owned projects

    project_dict = {
        'articles': [],
        'books': [],
        'translated_books': [],
        'research_proposals': [],
        'research_projects': [],
        'theses': [],
    }

    for project in user_projects:
        if isinstance(project, Article):
            project_dict['articles'].append(project)
        elif isinstance(project, Book):
            project_dict['books'].append(project)
        elif isinstance(project, TranslatedBook):
            project_dict['translated_books'].append(project)
        elif isinstance(project, ResearchProposal):
            project_dict['research_proposals'].append(project)
        elif isinstance(project, ResearchProject):
            project_dict['research_projects'].append(project)
        elif isinstance(project, Thesis):
            project_dict['theses'].append(project)

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
class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'

class BookCreateView(CreateView):
    model = Book
    template_name = 'book_form.html'
    fields = ['project', 'publisher', 'isbn', 'page_count', 'edition', 'preface', 'introduction', 'conclusion', 'bibliography', 'index', 'is_published']
    success_url = reverse_lazy('book_list')

class BookUpdateView(UpdateView):
    model = Book
    template_name = 'book_form.html'
    fields = ['project', 'publisher', 'isbn', 'page_count', 'edition', 'preface', 'introduction', 'conclusion', 'bibliography', 'index', 'is_published']
    success_url = reverse_lazy('book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

# TranslatedBook View
class TranslatedBookListView(ListView):
    model = TranslatedBook
    template_name = 'translated_book_list.html'
    context_object_name = 'translated_books'

class TranslatedBookDetailView(DetailView):
    model = TranslatedBook
    template_name = 'translated_book_detail.html'

class TranslatedBookCreateView(CreateView):
    model = TranslatedBook
    template_name = 'translated_book_form.html'
    fields = ['project', 'original_title', 'original_language', 'translator', 'publisher', 'isbn', 'page_count', 'is_published']
    success_url = reverse_lazy('translated_book_list')

class TranslatedBookUpdateView(UpdateView):
    model = TranslatedBook
    template_name = 'translated_book_form.html'
    fields = ['project', 'original_title', 'original_language', 'translator', 'publisher', 'isbn', 'page_count', 'is_published']
    success_url = reverse_lazy('translated_book_list')

class TranslatedBookDeleteView(DeleteView):
    model = TranslatedBook
    template_name = 'translated_book_confirm_delete.html'
    success_url = reverse_lazy('translated_book_list')

# Research Project Views
class ResearchProjectListView(ListView):
    model = ResearchProject
    template_name = 'projects/ResearchProject/researchproject_list.html'
    context_object_name = 'research_projects'

    def get_queryset(self):
        return ResearchProject.objects.select_related('owner').all()

class ResearchProjectDetailView(DetailView):
    model = ResearchProject
    template_name = 'projects/researchproject/researchproject_detail.html'
    context_object_name = 'research_project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.sections.all()
        return context

class ResearchProjectCreateView(LoginRequiredMixin, CreateView):
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'projects/researchproject/researchproject_create.html'
    success_url = reverse_lazy('research_project_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ResearchProjectUpdateView(UpdateView):
    model = ResearchProject
    template_name = 'projects/researchproject/researchproject_form.html'
    fields = ['title', 'description', 'organization', 'budget', 'funding_source', 'grant_number', 'template']
    success_url = reverse_lazy('research_project_list')

class ResearchProjectDeleteView(DeleteView):
    model = ResearchProject
    template_name = 'projects/researchproject/pesearchproject_confirm_delete.html'
    success_url = reverse_lazy('research_project_list')

# Thesis View
class ThesisListView(ListView):
    model = Thesis
    template_name = 'thesis_list.html'
    context_object_name = 'theses'

class ThesisDetailView(DetailView):
    model = Thesis
    template_name = 'thesis_detail.html'

class ThesisCreateView(CreateView):
    model = Thesis
    template_name = 'thesis_form.html'
    fields = ['project', 'student_name', 'university', 'department', 'degree_type', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ThesisUpdateView(UpdateView):
    model = Thesis
    template_name = 'thesis_form.html'
    fields = ['project', 'student_name', 'university', 'department', 'degree_type', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ThesisDeleteView(DeleteView):
    model = Thesis
    template_name = 'thesis_confirm_delete.html'
    success_url = reverse_lazy('thesis_list')

@require_POST
def add_reference_with_doi(request, pk):
    doi = request.POST.get('doi', '').strip()
    
    if not doi:
        return JsonResponse({'error': 'لطفاً DOI را وارد نمایید'}, status=400)
    
    try:
        project = get_object_or_404(Project, id=pk)
        existing_reference = Reference.objects.filter(doi=doi).first()
        
        if existing_reference:
            citation, created = Citation.objects.get_or_create(
                project=project,
                reference=existing_reference,
                defaults={'citation_text': f"منبع موجود با DOI: {doi}"}
            )
            
            if not created:
                return JsonResponse({
                    'success': True,
                    'error': 'این منبع قبلاً به پروژه اضافه شده بود',
                    'citation_key': existing_reference.citation_key
                })
            
            return JsonResponse({
                'success': True,
                'error': 'منبع موجود با موفقیت به پروژه اضافه شد',
                'citation_key': existing_reference.citation_key
            })
        
        cr = Crossref()
        work = cr.works(ids=doi)
        data = work['message']
        
        title = data.get('title', [''])[0]
        if not title:
            return JsonResponse({'error': 'مقاله با این DOI یافت نشد'}, status=404)
        
        authors = data.get('author', [])
        journal = data.get('container-title', [''])[0]
        published_date = data.get('published', {}).get('date-parts', [[None]])[0]
        year = published_date[0] if published_date else None
        
        article = Article.objects.create(
            title=title,
            article_type='research',
            abstract=data.get('abstract', ''),
            journal=journal,
            volume=data.get('volume', ''),
            issue=data.get('issue', ''),
            pages=data.get('page', ''),
            doi=doi,
            publish_date=f"{year}-01-01" if year else None,
            status='published'
        )
        
        for order, author_data in enumerate(authors, start=1):
            if not (author_data.get('given') and author_data.get('family')):
                continue
                
            author, _ = Author.objects.get_or_create(
                first_name=author_data.get('given', ''),
                last_name=author_data.get('family', ''),
                defaults={
                    'orcid_id': author_data.get('ORCID', ''),
                    'affiliation': ', '.join(author_data.get('affiliation', [])) 
                    if author_data.get('affiliation') else ''
                }
            )
            
            ArticleAuthorship.objects.create(
                article=article,
                author=author,
                authorship_order=order,
                is_corresponding=order == 1
            )
        
        reference = Reference.objects.create(
            citation_key=f"doi_{doi.replace('/', '_')}",
            reference_type='article',
            article=article,
            doi=doi
        )

        return JsonResponse({
            'success': True,
            'error': 'منبع جدید با موفقیت ایجاد و به پروژه اضافه شد',
            'citation_key': reference.citation_key,
            'title': title,
            'authors': ', '.join(
                f"{a.get('given', '')} {a.get('family', '')}" 
                for a in authors if a.get('given') and a.get('family')
            )
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'خطا در پردازش درخواست: {str(e)}'
        }, status=500)

def translate_text(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        target_lang = request.POST.get('target_lang', 'fa')
        
        try:
            translator = Translator(to_lang=target_lang)
            translation = translator.translate(text)
            return JsonResponse({'translation': translation})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'فقط درخواست POST مجاز است'}, status=400)