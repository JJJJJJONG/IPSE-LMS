from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings


class Contest(models.Model):
    title = models.CharField(max_length=200, verbose_name="대회명")
    description = models.TextField(blank=True, verbose_name="대회 설명")

    start_time = models.DateTimeField(verbose_name="시작 시간")
    end_time = models.DateTimeField(verbose_name="종료 시간")

    freeze_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="스코어보드 동결 시작 전(분)",
    )

    is_public = models.BooleanField(default=False, verbose_name="공개 여부")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["-start_time"]
        verbose_name = "대회"
        verbose_name_plural = "대회 목록"

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("종료 시간은 시작 시간보다 늦어야 합니다.")

    def freeze_start_time(self):
        return self.end_time - timedelta(minutes=self.freeze_minutes)

    def is_upcoming(self):
        now = timezone.now()
        return now < self.start_time

    def is_running(self):
        now = timezone.now()
        return self.start_time <= now < self.end_time

    def is_frozen(self):
        now = timezone.now()
        return self.is_running() and now >= self.freeze_start_time()

    def is_finished(self):
        now = timezone.now()
        return now >= self.end_time

    def status_label(self):
        if self.is_finished():
            return "종료"
        if self.is_frozen():
            return "동결 중"
        if self.is_running():
            return "진행 중"
        return "예정"

    def can_enter(self):
        now = timezone.now()
        return self.start_time <= now < self.end_time


class Problem(models.Model):
    title = models.CharField(max_length=200, verbose_name="문제명")
    slug = models.SlugField(unique=True, verbose_name="문제 코드")
    statement = models.TextField(verbose_name="문제 본문")

    input_description = models.TextField(blank=True, verbose_name="입력 설명")
    output_description = models.TextField(blank=True, verbose_name="출력 설명")

    sample_input = models.TextField(blank=True, verbose_name="예제 입력")
    sample_output = models.TextField(blank=True, verbose_name="예제 출력")

    time_limit = models.PositiveIntegerField(default=2, verbose_name="시간 제한(초)")
    memory_limit = models.PositiveIntegerField(default=256, verbose_name="메모리 제한(MB)")

    is_public = models.BooleanField(default=True, verbose_name="공개 여부")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        ordering = ["title"]
        verbose_name = "문제"
        verbose_name_plural = "문제 목록"

    def __str__(self):
        return self.title


class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="contest_problems",
        verbose_name="대회",
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="contest_links",
        verbose_name="문제",
    )
    label = models.CharField(max_length=10, verbose_name="문제 번호")
    order = models.PositiveIntegerField(default=0, verbose_name="정렬 순서")
    score = models.PositiveIntegerField(default=100, verbose_name="배점")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "대회 문제"
        verbose_name_plural = "대회 문제 목록"
        constraints = [
            models.UniqueConstraint(
                fields=["contest", "problem"],
                name="unique_contest_problem",
            ),
            models.UniqueConstraint(
                fields=["contest", "label"],
                name="unique_contest_label",
            ),
        ]

    def __str__(self):
        return f"{self.contest.title} - {self.label}"


class ContestParticipant(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="대회",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contest_participations",
        verbose_name="사용자",
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="참가 시각")
    is_active = models.BooleanField(default=True, verbose_name="참가 활성 상태")

    class Meta:
        verbose_name = "대회 참가자"
        verbose_name_plural = "대회 참가자 목록"
        constraints = [
            models.UniqueConstraint(
                fields=["contest", "user"],
                name="unique_contest_participant",
            ),
        ]

    def __str__(self):
        return f"{self.contest.title} - {self.user}"


SUBMISSION_RESULT_CHOICES = [
    ("PENDING", "채점 대기"),
    ("AC", "정답"),
    ("WA", "오답"),
    ("TLE", "시간 초과"),
    ("MLE", "메모리 초과"),
    ("RE", "런타임 에러"),
    ("CE", "컴파일 에러"),
]

LANGUAGE_CHOICES = [
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
]


class ContestSubmission(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="대회",
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="문제",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contest_submissions",
        verbose_name="사용자",
    )

    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default="python",
        verbose_name="제출 언어",
    )
    source_code = models.TextField(verbose_name="소스 코드")

    result = models.CharField(
        max_length=20,
        choices=SUBMISSION_RESULT_CHOICES,
        default="PENDING",
        verbose_name="채점 결과",
    )

    execution_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="실행 시간(ms)",
    )
    memory_kb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="메모리 사용량(KB)",
    )


    passed_count = models.PositiveIntegerField(default=0, verbose_name="통과 테스트 수")
    total_count = models.PositiveIntegerField(default=0, verbose_name="전체 테스트 수")
    judge_message = models.CharField(max_length=255, blank=True, verbose_name="채점 메시지")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="제출 시각")

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "대회 제출"
        verbose_name_plural = "대회 제출 목록"

    def __str__(self):
        return f"{self.contest.title} - {self.problem.title} - {self.user} - {self.result}"



class TestCase(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="testcases",
        verbose_name="문제",
    )
    input_data = models.TextField(verbose_name="입력 데이터")
    expected_output = models.TextField(verbose_name="기대 출력")
    is_sample = models.BooleanField(default=False, verbose_name="예제 여부")
    order = models.PositiveIntegerField(default=0, verbose_name="정렬 순서")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "테스트케이스"
        verbose_name_plural = "테스트케이스 목록"

    def __str__(self):
        return f"{self.problem.title} - 테스트케이스 {self.order}"


class SubmissionTestCaseResult(models.Model):
    submission = models.ForeignKey(
        ContestSubmission,
        on_delete=models.CASCADE,
        related_name="testcase_results",
        verbose_name="제출",
    )
    testcase = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        related_name="submission_results",
        verbose_name="테스트케이스",
    )
    passed = models.BooleanField(default=False, verbose_name="통과 여부")
    actual_output = models.TextField(blank=True, verbose_name="실제 출력")
    judge_message = models.CharField(max_length=255, blank=True, verbose_name="채점 메시지")

    class Meta:
        ordering = ["testcase__order", "id"]
        verbose_name = "제출 테스트케이스 결과"
        verbose_name_plural = "제출 테스트케이스 결과 목록"

    def __str__(self):
        return f"{self.submission.id} - TC {self.testcase.order} - {'PASS' if self.passed else 'FAIL'}"


class JudgeTask(models.Model):
    STATUS_CHOICES = [
        ("QUEUED", "대기 중"),
        ("RUNNING", "채점 중"),
        ("DONE", "완료"),
        ("FAILED", "실패"),
    ]

    submission = models.OneToOneField(
        ContestSubmission,
        on_delete=models.CASCADE,
        related_name="judge_task",
        verbose_name="제출",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="QUEUED",
        verbose_name="작업 상태",
    )
    error_message = models.TextField(blank=True, verbose_name="오류 메시지")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시각")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="시작 시각")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="완료 시각")

    class Meta:
        verbose_name = "채점 작업"
        verbose_name_plural = "채점 작업 목록"

    def __str__(self):
        return f"{self.submission.id} - {self.status}"