from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student

# 1. 기본 사용자(User) 관리 설정
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_lecturer')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_lecturer', 'gender', 'phone', 'address', 'picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_student', 'is_lecturer', 'gender', 'phone', 'address', 'picture')}),
    )

# 2. 학생(Student) 관리 설정
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_id_no')
    search_fields = ('student__username', 'student__first_name')

    def get_id_no(self, obj):
        return obj.student.username
    get_id_no.short_description = '학번'

# 관리자 페이지에 등록 (Parent, DepartmentHead 등은 삭제되었으므로 제외)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)