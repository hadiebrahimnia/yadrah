from django import forms
from Main.models import *
from django.contrib import messages
from django.shortcuts import redirect
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تنظیمات فیلدها
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'نام کاربری'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ایمیل'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تکرار رمز عبور'
        })
        
        # تنظیمات labelها
        self.fields['username'].label = 'نام کاربری'
        self.fields['email'].label = 'آدرس ایمیل'
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password2'].label = 'تأیید رمز عبور'
        
        # پیام‌های خطا
        self.fields['username'].help_text = 'حداکثر ۱۵۰ کاراکتر. فقط حروف، اعداد و @/./+/-/_ مجاز هستند.'


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تنظیمات فیلدهای فرم
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'کد ملی',
            'id': 'id_username'
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور',
            'id': 'id_password'
        })
        
        # تنظیمات labelها
        self.fields['username'].label = 'نام کاربری'
        self.fields['password'].label = 'رمز عبور'
        
        # تنظیمات error messages
        self.error_messages = {
            'invalid_login': "نام کاربری یا رمز عبور نادرست است.",
            'inactive': "این حساب غیرفعال است.",
        }

    class Meta:
        model = User
        fields = ("username", "password")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'type', 'status', 'progress', 'visibility',
            'start_date', 'end_date', 'keywords', 'tags', 'collaborators'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'keywords': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'collaborators': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'عنوان پروژه',
            'description': 'توضیحات',
            'type': 'نوع پروژه',
            'status': 'وضعیت',
            'progress': 'پیشرفت (درصد)',
            'visibility': 'قابلیت دید',
            'start_date': 'تاریخ شروع',
            'end_date': 'تاریخ پایان',
            'keywords': 'کلمات کلیدی',
            'tags': 'برچسب‌ها',
            'collaborators': 'همکاران',
        }


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = [
            'organization', 'research_code', 'supervisor', 'research_team',
            'budget', 'funding_source', 'grant_number', 'deliverables'
        ]
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
            'research_code': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'research_team': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'funding_source': forms.TextInput(attrs={'class': 'form-control'}),
            'grant_number': forms.TextInput(attrs={'class': 'form-control'}),
            'deliverables': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'organization': 'سازمان/دانشگاه',
            'research_code': 'کد پژوهشی',
            'supervisor': 'سرپرست',
            'research_team': 'تیم پژوهشی',
            'budget': 'بودجه (ریال)',
            'funding_source': 'منبع تأمین بودجه',
            'grant_number': 'شماره کمک مالی',
            'deliverables': 'محصولات پروژه',
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'article_type', 'subtitle', 'abstract', 'authors', 'status',
            'journal', 'volume', 'issue', 'pages', 'doi', 'is_published',
            'publish_date', 'manuscript', 'supplementary_materials', 'template'
        ]
        widgets = {
            'article_type': forms.Select(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'journal': forms.TextInput(attrs={'class': 'form-control'}),
            'volume': forms.TextInput(attrs={'class': 'form-control'}),
            'issue': forms.TextInput(attrs={'class': 'form-control'}),
            'pages': forms.TextInput(attrs={'class': 'form-control'}),
            'doi': forms.TextInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'publish_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manuscript': forms.FileInput(attrs={'class': 'form-control'}),
            'supplementary_materials': forms.FileInput(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'article_type': 'نوع مقاله',
            'subtitle': 'زیرعنوان',
            'abstract': 'چکیده',
            'authors': 'نویسندگان',
            'status': 'وضعیت',
            'journal': 'ژورنال/کنفرانس',
            'volume': 'جلد',
            'issue': 'شماره',
            'pages': 'صفحات',
            'doi': 'DOI',
            'is_published': 'منتشر شده؟',
            'publish_date': 'تاریخ انتشار',
            'manuscript': 'فایل مقاله',
            'supplementary_materials': 'مواد تکمیلی',
            'template': 'قالب مقاله',
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'publisher', 'isbn', 'isbn_13', 'page_count', 'edition', 'is_published',
            'cover_image', 'preface', 'introduction', 'conclusion', 'bibliography',
            'index', 'royalty_percentage', 'copyright_holder', 'copyright_year'
        ]
        widgets = {
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn_13': forms.TextInput(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'edition': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'preface': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'introduction': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'conclusion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'bibliography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'index': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'royalty_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'copyright_holder': forms.TextInput(attrs={'class': 'form-control'}),
            'copyright_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'publisher': 'ناشر',
            'isbn': 'ISBN',
            'isbn_13': 'ISBN-13',
            'page_count': 'تعداد صفحات',
            'edition': 'ویرایش',
            'is_published': 'منتشر شده؟',
            'cover_image': 'تصویر جلد',
            'preface': 'پیشگفتار',
            'introduction': 'مقدمه',
            'conclusion': 'نتیجه‌گیری',
            'bibliography': 'فهرست منابع',
            'index': 'شاخص',
            'royalty_percentage': 'درصد حق امتیاز',
            'copyright_holder': 'دارنده حق چاپ',
            'copyright_year': 'سال حق چاپ',
        }