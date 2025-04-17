from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from Main.models import *
from Main.forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from translate import Translator
from habanero import Crossref
from django.contrib.auth.decorators import login_required

# Main View
def home_page(request):
    return render(request, 'home/index.html', {
    })

def dashboard(request):
    # گرفتن پروژه‌های کاربر
    user_projects = request.user.projects.all()

    # دیکشنری برای ذخیره پروژه‌ها بر اساس نوع
    project_dict = {
        'articles': [],
        'books': [],
        'translated_books': [],
        'research_proposals': [],
        'research_projects': [],
        'theses': [],
    }

    # پر کردن دیکشنری با پروژه‌ها
    for project in user_projects:
        if project.type == 'article_writing':
            project_dict['articles'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })
        elif project.type == 'book_writing':
            project_dict['books'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })
        elif project.type == 'book_translation':
            project_dict['translated_books'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })
        elif project.type == 'research_proposal':
            project_dict['research_proposals'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })
        elif project.type == 'research_project':
            project_dict['research_projects'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })
        elif project.type == 'thesis':
            project_dict['theses'].append({
                'title': project.title,
                'type': project.get_type_display(),
            })

    return render(request, 'dashboard/dashboard.html', {
        'project_dict': project_dict,
    })


# Project View
class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'projects'

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'

class ProjectCreateView(CreateView):
    model = Project
    template_name = 'project_form.html'
    fields = ['title', 'description', 'type', 'status', 'start_date', 'end_date', 'owner', 'keywords', 'tags']
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'project_form.html'
    fields = ['title', 'description', 'type', 'status', 'start_date', 'end_date', 'owner', 'keywords', 'tags']
    success_url = reverse_lazy('project_list')

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('project_list')


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
    fields = ['project', 'author', 'comment_text']
    success_url = reverse_lazy('comment_list')

class ProjectCommentUpdateView(UpdateView):
    model = ProjectComment
    template_name = 'comment_form.html'
    fields = ['project', 'author', 'comment_text']
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


def article_create_with_doi(request):
    if request.method == 'POST':
        form = DOIArticleForm(request.POST)
        if form.is_valid():
            try:
                article = form.save(request)
                messages.success(request, "مقاله با موفقیت از طریق DOI وارد شد!")
                return redirect('article_detail', pk=article.pk)
            except Exception as e:
                messages.error(request, f"خطا در وارد کردن مقاله: {str(e)}")
                return redirect('article_create_with_doi')
    else:
        form = DOIArticleForm()
    
    return render(request, 'Project/Article/article_create_with_doi.html', {'form': form})


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


class ResearchProjectListView(ListView):
    model = ResearchProject
    template_name = 'Project/ResearchProject/ResearchProject_list.html'
    context_object_name = 'research_projects'

    def get_queryset(self):
        # استفاده از select_related برای بارگذاری اطلاعات مرتبط
        return ResearchProject.objects.select_related('project').all()

    def get_context_data(self, **kwargs):
        # فراخوانی متد والد
        context = super().get_context_data(**kwargs)
        # اضافه کردن لیست پروژه‌ها به context
        context['research_projects_list'] = self.get_queryset()
        return context


class ResearchProjectDetailView(DetailView):
    model = ResearchProject
    template_name = 'Project/ResearchProject/ResearchProject_detail.html'
    context_object_name = 'research_project'

    def get_object(self, queryset=None):
        # بارگذاری شیء بر اساس شناسه
        obj = super().get_object(queryset)
        return obj
    
    def get_context_data(self, **kwargs):
        # فراخوانی متد والد
        context = super().get_context_data(**kwargs)
        # اضافه کردن بخش‌های پروژه به context
        context['sections'] = self.object.sections.all()  # بارگذاری بخش‌ها
        return context

class ResearchProjectCreateView(CreateView):
    model = Thesis
    template_name = 'Project/ResearchProject/ResearchProject_form.html'
    # fields = ['project', 'student_name', 'university', 'department', 'degree', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ResearchProjectUpdateView(UpdateView):
    model = Thesis
    template_name = 'Project/ResearchProject/thesis_form.html'
    # fields = ['project', 'student_name', 'university', 'department', 'degree', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ResearchProjectDeleteView(DeleteView):
    model = ResearchProject
    template_name = 'Project/ResearchProject/ResearchProject_confirm_delete.html'
    success_url = reverse_lazy('ResearchProject_list')


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
    fields = ['project', 'student_name', 'university', 'department', 'degree', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ThesisUpdateView(UpdateView):
    model = Thesis
    template_name = 'thesis_form.html'
    fields = ['project', 'student_name', 'university', 'department', 'degree', 'defense_date']
    success_url = reverse_lazy('thesis_list')

class ThesisDeleteView(DeleteView):
    model = Thesis
    template_name = 'thesis_confirm_delete.html'
    success_url = reverse_lazy('thesis_list')



# Reference Views
class ReferenceListView(ListView):
    model = Reference
    template_name = 'reference_list.html'
    context_object_name = 'references'

class ReferenceDetailView(DetailView):
    model = Reference
    template_name = 'reference_detail.html'

class ReferenceCreateView(CreateView):
    model = Reference
    template_name = 'reference_form.html'
    fields = ['citation_key', 'reference_type', 'source_article', 'source_book', 'source_thesis']
    success_url = reverse_lazy('reference_list')

class ReferenceUpdateView(UpdateView):
    model = Reference
    template_name = 'reference_form.html'
    fields = ['citation_key', 'reference_type', 'source_article', 'source_book', 'source_thesis']
    success_url = reverse_lazy('reference_list')

class ReferenceDeleteView(DeleteView):
    model = Reference
    template_name = 'reference_confirm_delete.html'
    success_url = reverse_lazy('reference_list')

# Citation Views
class CitationListView(ListView):
    model = Citation
    template_name = 'citation_list.html'
    context_object_name = 'citations'

class CitationDetailView(DetailView):
    model = Citation
    template_name = 'citation_detail.html'

class CitationCreateView(CreateView):
    model = Citation
    template_name = 'citation_form.html'
    fields = ['project', 'reference', 'citation_text', 'page_number', 'location']
    success_url = reverse_lazy('citation_list')

class CitationUpdateView(UpdateView):
    model = Citation
    template_name = 'citation_form.html'
    fields = ['project', 'reference', 'citation_text', 'page_number', 'location']
    success_url = reverse_lazy('citation_list')

class CitationDeleteView(DeleteView):
    model = Citation
    template_name = 'citation_confirm_delete.html'
    success_url = reverse_lazy('citation_list')





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
