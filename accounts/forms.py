from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from .models import User, Student, GENDERS

class StaffAddForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

from django import forms
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student

# (기존의 StaffAddForm 등은 이 위에 그대로 둡니다)

class StudentSignUpForm(UserCreationForm):
    # 우리의 HTML UI에 맞춰서 학번(username)과 이메일만 요구하도록 세팅합니다.
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    # 기존 코드의 훌륭한 유산인 '트랜잭션 방어막'을 계승합니다.
    @transaction.atomic()
    def save(self, commit=True):
        # 1. 폼 데이터로 기본 User 객체 생성 (아직 DB 저장 전)
        user = super().save(commit=False)
        
        # 2. 이 유저는 IPSE 동아리원(학생)임을 명시
        user.is_student = True
        user.email = self.cleaned_data.get("email")
        
        if commit:
            # 3. User DB에 안전하게 저장
            user.save()
            # 4. 연결된 Student 프로필 DB 자동 생성
            Student.objects.create(student=user) 
            
        return user

# (기존의 ProfileUpdateForm 등은 이 아래에 그대로 둡니다)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()
            Student.objects.create(student=user) # Student 생성 시 Program 필드 제거 완료
        return user

class ProfileUpdateForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    gender = forms.CharField(widget=forms.Select(choices=GENDERS, attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "gender", "email", "phone", "address", "picture"]

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error("email", "해당 이메일로 등록된 사용자가 없습니다.")
            return email
            