from django.contrib import admin
from django.urls import path, include
from Main import views
from Main.models import *
from django.contrib.auth import views as auth_views
from tinymce.widgets import TinyMCE

urlpatterns = [
    # Home and Dashboard
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('', views.home_page, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    # # Articles
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/update/', views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),

    # # Books
    # path('books/', views.BookListView.as_view(), name='book_list'),
    # path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    # path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    # path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    # path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    # # Translated Books
    # path('translated-books/', views.TranslatedBookListView.as_view(), name='translated_book_list'),
    # path('translated-books/<int:pk>/', views.TranslatedBookDetailView.as_view(), name='translated_book_detail'),
    # path('translated-books/create/', views.TranslatedBookCreateView.as_view(), name='translated_book_create'),
    # path('translated-books/<int:pk>/update/', views.TranslatedBookUpdateView.as_view(), name='translated_book_update'),
    # path('translated-books/<int:pk>/delete/', views.TranslatedBookDeleteView.as_view(), name='translated_book_delete'),

    # # Research Proposals
    # path('research-proposals/', views.ResearchProposalListView.as_view(), name='research_proposal_list'),
    # path('research-proposals/<int:pk>/', views.ResearchProposalDetailView.as_view(), name='research_proposal_detail'),
    # path('research-proposals/create/', views.ResearchProposalCreateView.as_view(), name='research_proposal_create'),
    # path('research-proposals/<int:pk>/update/', views.ResearchProposalUpdateView.as_view(), name='research_proposal_update'),
    # path('research-proposals/<int:pk>/delete/', views.ResearchProposalDeleteView.as_view(), name='research_proposal_delete'),

    # Research Projects
    path('research-projects/', views.ResearchProjectListView.as_view(), name='research_project_list'),
    path('research-projects/create/', views.ResearchProjectCreateView.as_view(), name='research_project_create'),
    path('research-projects/<int:pk>/', views.ResearchProjectDetailView.as_view(), name='research_project_detail'),
    path('research-projects/<int:pk>/update/', views.ResearchProjectUpdateView.as_view(), name='research_project_update'),
    path('research-projects/<int:pk>/delete/', views.ResearchProjectDeleteView.as_view(), name='research_project_delete'),

    # # Theses
    # path('theses/', views.ThesisListView.as_view(), name='thesis_list'),
    # path('theses/<int:pk>/', views.ThesisDetailView.as_view(), name='thesis_detail'),
    # path('theses/create/', views.ThesisCreateView.as_view(), name='thesis_create'),
    # path('theses/<int:pk>/update/', views.ThesisUpdateView.as_view(), name='thesis_update'),
    # path('theses/<int:pk>/delete/', views.ThesisDeleteView.as_view(), name='thesis_delete'),

    # References
    path('<str:content_type>/<int:object_id>/references/add-with-doi/', views.add_reference_with_doi, name='add_reference_with_doi'),

    # # Tasks
    # path('tasks/', views.TaskListView.as_view(), name='task_list'),
    # path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    # path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    # path('tasks/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    # path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # # Project Comments
    # path('comments/', views.ProjectCommentListView.as_view(), name='comment_list'),
    # path('comments/<int:pk>/', views.ProjectCommentDetailView.as_view(), name='comment_detail'),
    # path('comments/create/', views.ProjectCommentCreateView.as_view(), name='comment_create'),
    # path('comments/<int:pk>/update/', views.ProjectCommentUpdateView.as_view(), name='comment_update'),
    # path('comments/<int:pk>/delete/', views.ProjectCommentDeleteView.as_view(), name='comment_delete'),

    # # Notifications
    # path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    # path('notifications/<int:pk>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),

    # Translation API
    path('translate/', views.translate_text, name='translate_text'),
]