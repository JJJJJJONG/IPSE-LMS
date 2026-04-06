from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save
from .utils import unique_slug_generator

# ==========================================
# 1. 강의 카테고리 (3대 카테고리 + 테마 컬러)
# ==========================================
class CourseCategory(models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name="트랙 이름")
    summary = models.TextField(null=True, blank=True, verbose_name="트랙 설명")
    # 🚨 카테고리별 고유 색상을 저장하는 필드 추가 (예: #3b82f6)
    theme_color = models.CharField(max_length=20, default="bg-blue-500", help_text="Tailwind 색상 클래스 입력 (예: bg-blue-500)")

    def __str__(self):
        return self.title

# ==========================================
# 2. 핵심 강의 모델 (난이도 삭제)
# ==========================================
class Course(models.Model):
    slug = models.SlugField(blank=True, unique=True)
    title = models.CharField(max_length=200, verbose_name="강의명")
    code = models.CharField(max_length=50, unique=True, verbose_name="강의 코드")
    summary = models.TextField(blank=True, null=True, verbose_name="강의 요약")
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, verbose_name="소속 트랙")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="담당 강사/운영진")
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True, verbose_name="강의 썸네일")

    def __str__(self):
        return f"[{self.category.title}] {self.title}"

    def get_absolute_url(self):
        return reverse("course_detail", kwargs={"slug": self.slug})

def course_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
pre_save.connect(course_pre_save_receiver, sender=Course)

# ==========================================
# 3. 강의 자료 (파일) 업로드
# ==========================================
class Upload(models.Model):
    title = models.CharField(max_length=100, verbose_name="자료명")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="course_files/",
        help_text="허용 확장자: pdf, docx, xls, ppt, zip, rar, 7zip 등",
        validators=[FileExtensionValidator(["pdf", "docx", "doc", "xls", "xlsx", "ppt", "pptx", "zip", "rar", "7zip"])]
    )
    upload_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

# ==========================================
# 4. 강의 영상 업로드
# ==========================================
class UploadVideo(models.Model):
    title = models.CharField(max_length=100, verbose_name="영상 제목")
    slug = models.SlugField(blank=True, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to="course_videos/",
        validators=[FileExtensionValidator(["mp4", "mkv", "wmv", "3gp", "f4v", "avi", "mp3"])]
    )
    summary = models.TextField(null=True, blank=True, verbose_name="영상 요약")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

def video_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
pre_save.connect(video_pre_save_receiver, sender=UploadVideo)

# ==========================================
# 5. [신규] 동아리원 진도율 추적 모델
# ==========================================
class UserCourseProgress(models.Model):
    # 🚨 'User' 대신 'settings.AUTH_USER_MODEL'을 사용하여 커스텀 유저와 연결합니다.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField('Lesson', blank=True)
    
    @property
    def progress_percentage(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        # 🚨 완료된 수업 수 / 전체 수업 수 * 100
        return int((self.completed_lessons.count() / total_lessons) * 100)

    class Meta:

        unique_together = ('user', 'course')

# ==========================================
# 6. [신규] 강의 단원과 수업 모델
# ==========================================
class Unit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units', verbose_name="소속 강의")
    title = models.CharField(max_length=200, verbose_name="단원명 (예: SECCOMP)")
    order = models.IntegerField(default=0, verbose_name="정렬 순서")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ==========================================
# 7. [신규] 강의 수업 모델 (Lesson과 Course연결)
# ==========================================
class Lesson(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="소속 강의")
    title = models.CharField(max_length=200, verbose_name="수업명 (예: Background: SECCOMP)")
    content = models.TextField(verbose_name="강의 내용 (HTML/Markdown)")
    order = models.IntegerField(default=0, verbose_name="정렬 순서")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        # 🚨 self.unit.course.slug 대신 self.course.slug 로 단축
        return reverse("lesson_detail", kwargs={"course_slug": self.course.slug, "lesson_pk": self.pk})

