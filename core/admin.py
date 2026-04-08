from django.contrib import admin

from .models import ActivityLog, Schedule


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action_type", "course", "created_at")
    list_filter = ("action_type", "created_at")
    search_fields = ("user__username", "message", "course__title")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "is_global", "start_date", "end_date")
    list_filter = ("is_global", "start_date")
    search_fields = ("title", "description", "user__username")
