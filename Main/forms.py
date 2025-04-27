from django import forms
from Main.models import *
from django.contrib import messages
from django.shortcuts import redirect
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()

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
            'start_date', 'end_date', 'collaborators', 'related_projects'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان پروژه را وارد کنید'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'توضیحات پروژه'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'project-type'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control select2',
                'id': 'project-status'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 5
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'start-date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'end-date'
            }),
            'collaborators': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple',
                'id': 'project-collaborators'
            }),
            'related_projects': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple',
                'id': 'related-projects'
            }),
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
            'collaborators': 'همکاران',
            'related_projects': 'پروژه‌های مرتبط',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # فیلتر همکاران - نمایش همه کاربران به جز خود کاربر
        if user:
            self.fields['collaborators'].queryset = User.objects.exclude(id=user.id)
            self.fields['related_projects'].queryset = Project.objects.filter(
                Q(owner=user) | Q(collaborators=user)
            ).distinct().exclude(id=self.instance.id) if self.instance else Project.objects.filter(
                Q(owner=user) | Q(collaborators=user)
            ).distinct()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد")

        return cleaned_data


class ResearchProjectForm(forms.ModelForm):
    """
    فرم یکپارچه برای ایجاد و ویرایش طرح پژوهشی
    """
    use_template = forms.BooleanField(
        required=False,
        initial=False,
        label='استفاده از قالب',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='برای استفاده از ساختار از پیش تعریف شده'
    )

    class Meta:
        model = ResearchProject
        fields = [
            'project','organization', 'research_code',
            'supervisor', 'research_team', 'budget', 'funding_source',
            'grant_number', 'deliverables', 'research_project_status'
        ]
        
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'انتخاب پروژه'
            }),
            
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام سازمان یا دانشگاه'
            }),
            'research_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کد پژوهشی'
            }),
            'supervisor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام سرپرست طرح'
            }),
            'research_team': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple',
                'data-placeholder': 'انتخاب اعضای تیم'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مبلغ به ریال'
            }),
            'funding_source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'منبع تأمین مالی'
            }),
            'grant_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره گرنت'
            }),
            'deliverables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'خروجی‌های مورد انتظار'
            }),
            
        }
        labels = {
            'project': ' پروژه',
            'organization': 'سازمان متولی',
            'research_code': 'کد پژوهشی',
            'supervisor': 'سرپرست طرح',
            'research_team': 'اعضای تیم',
            'budget': 'بودجه (ریال)',
            'funding_source': 'منبع مالی',
            'grant_number': 'شماره گرنت',
            'deliverables': 'خروجی‌ها',
        }
        help_texts = {
            'research_code': 'کد یکتا اختصاص داده شده به طرح',
            'grant_number': 'شماره‌ای که حامی مالی به طرح اختصاص داده است'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.edit_mode = kwargs.pop('edit_mode', False)
        super().__init__(*args, **kwargs)

        # تنظیمات خاص برای حالت ویرایش
        if self.edit_mode:
            if self.instance.pk and self.instance.research_project_status != 'draft':
                for field in ['title', 'organization', 'research_code']:
                    self.fields[field].disabled = True

            # در حالت ویرایش، فیلد قالب را فقط اگر طرح از قالب استفاده نکرده باشد نمایش می‌دهیم
            if not self.instance.template:
                self.fields['use_template'].initial = False
                self.fields['template'] = forms.ModelChoiceField(
                    queryset=ResearchProjectTemplate.objects.all(),
                    widget=forms.Select(attrs={'class': 'form-control'}),
                    label='قالب طرح',
                    required=False
                )
            else:
                self.fields['use_template'].widget = forms.HiddenInput()
        else:
            # در حالت ایجاد، فیلد قالب را به صورت مشروط نمایش می‌دهیم
            self.fields['template'] = forms.ModelChoiceField(
                queryset=ResearchProjectTemplate.objects.all(),
                widget=forms.Select(attrs={'class': 'form-control'}),
                label='قالب طرح',
                required=False
            )
            self.fields['research_project_status'].initial = 'draft'
            self.fields['research_project_status'].widget = forms.HiddenInput()

        # فیلتر کردن اعضای تیم
        self.fields['research_team'].queryset = Author.objects.filter(user__is_active=True)

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget and budget < 0:
            raise forms.ValidationError("بودجه نمی‌تواند مقدار منفی داشته باشد.")
        return budget

    def clean(self):
        cleaned_data = super().clean()
        use_template = cleaned_data.get('use_template')
        
        if use_template and not cleaned_data.get('template'):
            self.add_error('template', 'در صورت انتخاب گزینه استفاده از قالب، باید یک قالب مشخص شود.')
        
        return cleaned_data