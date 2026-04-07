from django.contrib import admin

from .models import (
    Contest,
    Problem,
    ContestProblem,
    ContestParticipant,
    ContestSubmission,
    TestCase,
    SubmissionTestCaseResult,
    JudgeTask,
)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "start_time",
        "end_time",
        "freeze_minutes",
        "is_public",
        "is_active",
    )
    list_filter = ("is_public", "is_active")
    search_fields = ("title", "description")


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "time_limit",
        "memory_limit",
        "is_public",
    )
    list_filter = ("is_public",)
    search_fields = ("title", "slug", "statement")


@admin.register(ContestProblem)
class ContestProblemAdmin(admin.ModelAdmin):
    list_display = (
        "contest",
        "label",
        "problem",
        "order",
        "score",
    )
    list_filter = ("contest",)
    search_fields = ("contest__title", "problem__title", "label")


@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "contest",
        "user",
        "joined_at",
        "is_active",
    )
    list_filter = ("contest", "is_active")
    search_fields = ("contest__title", "user__username")


@admin.register(ContestSubmission)
class ContestSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "contest",
        "problem",
        "user",
        "language",
        "result",
        "submitted_at",
    )
    list_filter = ("contest", "language", "result")
    search_fields = ("contest__title", "problem__title", "user__username")


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = (
        "problem",
        "order",
        "is_sample",
    )
    list_filter = ("is_sample", "problem")
    search_fields = ("problem__title",)


@admin.register(SubmissionTestCaseResult)
class SubmissionTestCaseResultAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "testcase",
        "passed",
    )
    list_filter = ("passed", "testcase__problem")
    search_fields = ("submission__user__username", "testcase__problem__title")


@admin.register(JudgeTask)
class JudgeTaskAdmin(admin.ModelAdmin):
    list_display = (
        "submission",
        "status",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status",)
    search_fields = ("submission__user__username", "submission__problem__title")