from django.contrib import admin
from django.urls import path, include
from Main import views

urlpatterns = [
    # Home and Dashboard
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),


    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # Articles
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('references/add-with-doi/', views.add_reference_with_doi, name='add_reference_with_doi'),
    
    # Books
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    # Translated Books
    path('translated-books/', views.TranslatedBookListView.as_view(), name='translated_book_list'),
    path('translated-books/<int:pk>/', views.TranslatedBookDetailView.as_view(), name='translated_book_detail'),
    path('translated-books/create/', views.TranslatedBookCreateView.as_view(), name='translated_book_create'),
    path('translated-books/<int:pk>/update/', views.TranslatedBookUpdateView.as_view(), name='translated_book_update'),
    path('translated-books/<int:pk>/delete/', views.TranslatedBookDeleteView.as_view(), name='translated_book_delete'),


    # ResearchProject
    path('ResearchProject/', views.ResearchProjectListView.as_view(), name='ResearchProject_list'),
    path('ResearchProject/<int:pk>/', views.ResearchProjectDetailView.as_view(), name='ResearchProject_detail'),
    path('ResearchProject/create/', views.ResearchProjectCreateView.as_view(), name='ResearchProject_create'),
    path('ResearchProject/<int:pk>/update/', views.ResearchProjectUpdateView.as_view(), name='ResearchProject_update'),
    path('ResearchProject/<int:pk>/delete/', views.ResearchProjectDeleteView.as_view(), name='ResearchProject_delete'),

    # Theses
    path('theses/', views.ThesisListView.as_view(), name='thesis_list'),
    path('theses/<int:pk>/', views.ThesisDetailView.as_view(), name='thesis_detail'),
    path('theses/create/', views.ThesisCreateView.as_view(), name='thesis_create'),
    path('theses/<int:pk>/update/', views.ThesisUpdateView.as_view(), name='thesis_update'),
    path('theses/<int:pk>/delete/', views.ThesisDeleteView.as_view(), name='thesis_delete'),
    

    # References
    path('references/', views.ReferenceListView.as_view(), name='reference_list'),
    path('references/<int:pk>/', views.ReferenceDetailView.as_view(), name='reference_detail'),
    path('references/create/', views.ReferenceCreateView.as_view(), name='reference_create'),
    path('references/<int:pk>/update/', views.ReferenceUpdateView.as_view(), name='reference_update'),
    path('references/<int:pk>/delete/', views.ReferenceDeleteView.as_view(), name='reference_delete'),

    # Citations
    path('citations/', views.CitationListView.as_view(), name='citation_list'),
    path('citations/<int:pk>/', views.CitationDetailView.as_view(), name='citation_detail'),
    path('citations/create/', views.CitationCreateView.as_view(), name='citation_create'),
    path('citations/<int:pk>/update/', views.CitationUpdateView.as_view(), name='citation_update'),
    path('citations/<int:pk>/delete/', views.CitationDeleteView.as_view(), name='citation_delete'),

    # Tasks
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # Project Comments
    path('comments/', views.ProjectCommentListView.as_view(), name='comment_list'),
    path('comments/<int:pk>/', views.ProjectCommentDetailView.as_view(), name='comment_detail'),
    path('comments/create/', views.ProjectCommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:pk>/update/', views.ProjectCommentUpdateView.as_view(), name='comment_update'),
    path('comments/<int:pk>/delete/', views.ProjectCommentDeleteView.as_view(), name='comment_delete'),

    path('translate/', views.translate_text, name='translate_text'),
]