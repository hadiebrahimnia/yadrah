from django import forms
from Main.models import *
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from habanero import Crossref
from datetime import date
from Main.models import Article, Author, ArticleAuthorship, Project, Keyword


class DOIArticleForm(forms.Form):
    doi = forms.CharField(
        label='DOI',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., 10.1038/s41586-019-1666-5',
            'class': 'form-control'
        })
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(type='article_writing'),
        label='Associated Project',
        required=False,
        help_text='Select an existing article writing project or leave blank to create a new one'
    )
    
    create_new_project = forms.BooleanField(
        label='Create new project',
        required=False,
        help_text='Check to create a new project for this article'
    )
    
    new_project_title = forms.CharField(
        label='New Project Title',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        doi = cleaned_data.get('doi')
        create_new_project = cleaned_data.get('create_new_project')
        new_project_title = cleaned_data.get('new_project_title')
        project = cleaned_data.get('project')
        
        # Validate DOI format
        if doi and not doi.startswith('10.'):
            raise forms.ValidationError("Please enter a valid DOI starting with '10.'")
            
        # Validate project selection
        if create_new_project and not new_project_title:
            raise forms.ValidationError("Please provide a title for the new project")
        elif not create_new_project and not project:
            raise forms.ValidationError("Please select an existing project or choose to create a new one")
            
        return cleaned_data

    def save(self, request):
        doi = self.cleaned_data['doi']
        cr = Crossref()
        
        try:
            # Fetch article data from Crossref
            work = cr.works(ids=doi)
            message = work['message']
            
            # Get or create project
            if self.cleaned_data['create_new_project']:
                project = Project.objects.create(
                    title=self.cleaned_data['new_project_title'],
                    type='article_writing',
                    status='completed',
                    owner=request.user
                )
            else:
                project = self.cleaned_data['project']
            
            # Parse publication date
            pub_date = None
            date_data = message.get('published-print', message.get('published-online', {}))
            if date_data and 'date-parts' in date_data and date_data['date-parts']:
                date_parts = date_data['date-parts'][0]
                if len(date_parts) >= 1:
                    year = date_parts[0]
                    month = date_parts[1] if len(date_parts) > 1 else 1
                    day = date_parts[2] if len(date_parts) > 2 else 1
                    pub_date = date(year, month, day)
            
            # Create article
            article = Article.objects.create(
                project=project,
                title=message.get('title', [''])[0],
                abstract=message.get('abstract', ''),
                article_type='research',
                status='published',
                journal=message.get('container-title', [''])[0],
                volume=message.get('volume', ''),
                issue=message.get('issue', ''),
                pages=message.get('page', ''),
                doi=doi,
                is_published=True,
                publish_date=pub_date
            )
            
            # Process authors
            for author_data in message.get('author', []):
                author, created = Author.objects.get_or_create(
                    first_name=author_data.get('given', ''),
                    last_name=author_data.get('family', ''),
                    defaults={
                        'orcid_id': author_data.get('ORCID', ''),
                        'affiliation': ', '.join(author_data.get('affiliation', [])) if author_data.get('affiliation') else ''
                    }
                )
                
                # Create authorship record
                ArticleAuthorship.objects.create(
                    article=article,
                    author=author,
                    is_corresponding='corresponding' in author_data.get('sequence', '').lower(),
                    authorship_order=message['author'].index(author_data) + 1
                )
            
            # Process keywords/subjects
            if 'subject' in message:
                for subject in message['subject']:
                    keyword, created = Keyword.objects.get_or_create(term=subject[:100])  # Truncate to 100 chars
                    article.keywords.add(keyword)
            
            messages.success(request, f"Article '{article.title}' was successfully imported!")
            return article
            
        except Exception as e:
            messages.error(request, f"Error importing DOI: {str(e)}")
            raise  # Re-raise the exception after showing error message

    def _parse_date(self, date_data):
        """Helper method to parse date from Crossref data"""
        if not date_data or 'date-parts' not in date_data:
            return None
            
        date_parts = date_data['date-parts'][0]
        if not date_parts:
            return None
            
        year = date_parts[0] if len(date_parts) > 0 else None
        month = date_parts[1] if len(date_parts) > 1 else 1
        day = date_parts[2] if len(date_parts) > 2 else 1
        
        if year:
            return date(year, month, day)
        return None