from django.contrib import admin
from .models import CourseCategory, Course, Upload, UploadVideo, UserCourseProgress, Lesson

# IPSE LMS 맞춤형 모델 등록
admin.site.register(CourseCategory)
admin.site.register(Upload)
admin.site.register(UploadVideo)
admin.site.register(UserCourseProgress)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "code", "category", "instructor", "enrollment_deadline"]
    list_filter = ["category", "enrollment_deadline"]
    search_fields = ["title", "code"]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    ordering = ['course', 'order']