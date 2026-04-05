from django.contrib import admin
from .models import CourseCategory, Course, Upload, UploadVideo, UserCourseProgress

# IPSE LMS 맞춤형 모델 등록
admin.site.register(CourseCategory)
admin.site.register(Course)
admin.site.register(Upload)
admin.site.register(UploadVideo)
admin.site.register(UserCourseProgress)