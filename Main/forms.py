from django import forms
from Main.models import *
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from habanero import Crossref
from datetime import date
from Main.models import Article, Author, ArticleAuthorship, Project, Keyword

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'status', 'start_date', 'end_date', 'keywords', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'keywords': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'عنوان پروژه',
            'description': 'توضیحات',
            'type': 'نوع پروژه',
            'status': 'وضعیت',
            'start_date': 'تاریخ شروع',
            'end_date': 'تاریخ پایان',
            'keywords': 'کلمات کلیدی',
            'tags': 'برچسب‌ها',
        }







class DOIReferenceForm(forms.Form):
    doi = forms.CharField(
        label='DOI',
        max_length=255,
        required=True,
        help_text='لطفاً DOI مقاله را وارد کنید (مثال: 10.1234/abc.2021.11)'
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        label='پروژه مرتبط',
        required=False
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(owner=user)



