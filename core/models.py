from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings  
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

class Schedule(models.Model):
    """동아리 및 개인 일정 모델"""
    title = models.CharField(max_length=200, verbose_name="일정명")
    description = models.TextField(blank=True, null=True, verbose_name="상세 내용")
    start_date = models.DateTimeField(verbose_name="시작 일시")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="종료 일시")
    
    # 누가 작성했는지 기록
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # True면 동아리 전체 일정(관리자만 생성 가능), False면 개인 일정
    is_global = models.BooleanField(default=False, verbose_name="동아리 전체 일정 여부")

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{'[전체]' if self.is_global else '[개인]'} {self.title}"