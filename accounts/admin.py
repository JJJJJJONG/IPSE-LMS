from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student


@admin.action(description="선택한 사용자 계정을 승인합니다 (is_active=True)")
def approve_users(modeladmin, request, queryset):
    updated = queryset.filter(is_active=False).update(is_active=True)
    modeladmin.message_user(request, f"{updated}명의 계정이 승인되었습니다.")


@admin.action(description="선택한 사용자 계정을 비활성화합니다 (is_active=False)")
def deactivate_users(modeladmin, request, queryset):
    updated = queryset.filter(is_active=True).update(is_active=False)
    modeladmin.message_user(request, f"{updated}명의 계정이 비활성화되었습니다.")


# 1. 기본 사용자(User) 관리 설정
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_student', 'is_lecturer', 'is_staff')
    list_filter = ('is_active', 'is_student', 'is_lecturer', 'is_staff')
    actions = [approve_users, deactivate_users]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_student', 'is_lecturer', 'gender', 'phone', 'address', 'picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_student', 'is_lecturer', 'gender', 'phone', 'address', 'picture')}),
    )


# 2. 학생(Student) 관리 설정
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_id_no', 'get_is_active')
    list_filter = ('student__is_active',)
    search_fields = ('student__username', 'student__first_name')

    def get_id_no(self, obj):
        return obj.student.username
    get_id_no.short_description = '학번'

    def get_is_active(self, obj):
        return obj.student.is_active
    get_is_active.short_description = '승인 여부'
    get_is_active.boolean = True


# 관리자 페이지에 등록
admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)