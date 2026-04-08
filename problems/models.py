from django.db import models
from django.conf import settings
from django.urls import reverse
from course.models import CourseCategory
import os


class Problem(models.Model):
    DIFFICULTY_CHOICES = [(i, f"Level {i}") for i in range(1, 11)]

    title = models.CharField(max_length=200, verbose_name="문제 제목")
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="분야",
    )
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=1,
        verbose_name="난이도",
    )
    points = models.IntegerField(default=100, verbose_name="보상 포인트")
    description = models.TextField(verbose_name="문제 설명")
    flag = models.CharField(max_length=100, verbose_name="정답(Flag)")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="출제자",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        category_title = self.category.title if self.category else "미분류"
        return f"[{category_title}] {self.title}"

    def get_absolute_url(self):
        return reverse("problem_detail", kwargs={"pk": self.pk})


class SolveRecord(models.Model):
    STATUS_CHOICES = [
        ("TODO", "시도 전"),
        ("ATTEMPT", "시도 중"),
        ("SOLVED", "해결"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solve_records",
    )
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="TODO")
    solved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "problem")
        ordering = ["-solved_at"]

    def __str__(self):
        return f"{self.user} - {self.problem} - {self.status}"


class ProblemAttachment(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(upload_to="problem_files/", verbose_name="첨부파일")

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class ProblemComment(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} - {self.problem}"