from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from PIL import Image
from .validators import ASCIIUsernameValidator

class CustomUserManager(UserManager):
    """IPSE 동아리원 검색 및 통계를 위한 매니저"""
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

    def get_student_count(self):
        return self.model.objects.filter(is_student=True).count()

    def get_lecturer_count(self):
        return self.model.objects.filter(is_lecturer=True).count()

GENDERS = ((_("M"), _("Male")), (_("F"), _("Female")))

class User(AbstractUser):
    """
    IPSE의 통합 유저 모델
    - first_name, last_name의 필수 조건을 해제하여 가입 절차를 간소화함
    """
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    
    # 🚨 핵심 수정: null=True, blank=True를 추가하여 DB 제약 조건을 해제합니다.
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True)
    email = models.EmailField(blank=True, null=True)

    username_validator = ASCIIUsernameValidator()
    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    @property
    def get_full_name(self):
        """이름이 없을 경우 학번(ID)을 반환하여 시스템 에러를 방지합니다."""
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return self.username

    def __str__(self):
        return f"{self.username} ({self.get_full_name})"

    def get_picture(self):
        try:
            return self.picture.url
        except:
            return settings.MEDIA_URL + "default.png"

    def save(self, *args, **kwargs):
        """프로필 이미지 최적화 로직 유지"""
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.picture.path)
        except:
            pass

class Student(models.Model):
    """IPSE 동아리원(학생) 상세 정보 모델"""
    student = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        return self.student.get_full_name