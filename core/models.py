from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.conf import settings  
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

NEWS = _("News")
EVENTS = _("Event")

POST = (
    (NEWS, _("News")),
    (EVENTS, _("Event")),
)

# ... (기존 FIRST, SECOND, SEMESTER, Manager 클래스들은 잔재일 수 있으나 에러 방지를 위해 그대로 유지) ...
FIRST = _("First")
SECOND = _("Second")
THIRD = _("Third")

SEMESTER = (
    (FIRST, _("First")),
    (SECOND, _("Second")),
    (THIRD, _("Third")),
)

class NewsAndEventsQuerySet(models.query.QuerySet):
    def search(self, query):
        lookups = (
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(posted_as__icontains=query)
        )
        return self.filter(lookups).distinct()

class NewsAndEventsManager(models.Manager):
    def get_queryset(self):
        return NewsAndEventsQuerySet(self.model, using=self._db)
    def all(self): return self.get_queryset()
    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)
        if qs.count() == 1: return qs.first()
        return None
    def search(self, query): return self.get_queryset().search(query)


# 💡 업그레이드 1: 공지사항 및 행사 (Notice & Calendar)
class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True, verbose_name="제목")
    summary = models.TextField(max_length=200, blank=True, null=True, verbose_name="내용 요약")
    posted_as = models.CharField(choices=POST, max_length=10, verbose_name="게시글 분류")
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    
    # 달력을 위해 새로 추가한 필드!
    event_date = models.DateField(null=True, blank=True, verbose_name="행사 진행 일자 (Event용)")

    objects = NewsAndEventsManager()

    def __str__(self):
        return self.title

# 💡 업그레이드 2: 활동 내역 타임라인 (Activity Feed)
class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('COURSE', '강의 수강'),
        ('PROBLEM', '문제 풀이'),
        ('SYSTEM', '시스템 알림'),
    )
    
    # 기존 모델에 개인화(Personalization) 필드 추가
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities', null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='SYSTEM')
    
    message = models.TextField(verbose_name="활동 내역")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "시스템"
        return f"[{self.created_at}] {username} - {self.message}"

# ... (기존 Session, Semester 모델은 하단에 그대로 유지) ...
class Session(models.Model):
    session = models.CharField(max_length=200, unique=True)
    is_current_session = models.BooleanField(default=False, blank=True, null=True)
    next_session_begins = models.DateField(blank=True, null=True)
    def __str__(self): return self.session

class Semester(models.Model):
    semester = models.CharField(max_length=10, choices=SEMESTER, blank=True)
    is_current_semester = models.BooleanField(default=False, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, blank=True, null=True)
    next_semester_begins = models.DateField(null=True, blank=True)
    def __str__(self): return self.semester

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