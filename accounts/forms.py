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

class StudentSignUpForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        max_length=20,
        label="학번",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "학번을 입력하세요"
        })
    )
    nickname = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "닉네임을 입력하세요"
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "이메일을 입력하세요"
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "nickname", "email")

    def clean_username(self):
        student_id = self.cleaned_data.get("username", "").strip()

        if not student_id.isdigit():
            raise forms.ValidationError("학번 형식으로 입력해주세요.")

        if Student.objects.filter(student_number=int(student_id)).exists():
            raise forms.ValidationError("이미 등록된 학번입니다.")

        return student_id

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.username = self.cleaned_data.get("username", "").strip()
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()
            # post_save 시그널이 이미 빈 Student를 생성하므로, 생성 대신 업데이트
            student = user.student
            student.student_number = int(self.cleaned_data.get("username").strip())
            student.nickname = self.cleaned_data.get("nickname", "").strip()
            student.save()

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
            