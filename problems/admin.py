from django.contrib import admin
from .models import Problem, SolveRecord

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    # 관리자 목록에서 보여줄 필드들
    list_display = ('title', 'category', 'difficulty', 'points', 'author', 'created_at')
    # 우측 필터 바 설정
    list_filter = ('category', 'difficulty')
    # 검색 기능
    search_fields = ('title', 'description')
    # 난이도순 정렬
    ordering = ('difficulty', 'title')

@admin.register(SolveRecord)
class SolveRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'solved_at')
    list_filter = ('status',)