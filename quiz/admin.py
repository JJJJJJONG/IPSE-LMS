from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from .models import (
    Quiz,
    Progress,
    Question,
    MCQuestion,
    Choice,
    EssayQuestion,
    Sitting,
)

# ------------------------------------------------------------------------------
# 1. Choice Inline (문제 안에서 선택지를 바로 수정할 수 있게 함)
# ------------------------------------------------------------------------------
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4  # 기본적으로 4개의 선택지 입력 칸을 보여줌

# ------------------------------------------------------------------------------
# 2. Quiz Admin Form (퀴즈와 문제 간의 다대다 관계 관리)
# ------------------------------------------------------------------------------
class QuizAdminForm(forms.ModelForm): # TranslationModelForm에서 forms.ModelForm으로 변경
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(verbose_name=_("Questions"), is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["questions"].initial = self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data["questions"])
        self.save_m2m()
        return quiz

# ------------------------------------------------------------------------------
# 3. Quiz Admin
# ------------------------------------------------------------------------------
class QuizAdmin(admin.ModelAdmin): # TranslationAdmin에서 admin.ModelAdmin으로 변경
    form = QuizAdminForm
    fields = ('title', 'description',)
    list_display = ("title",)
    search_fields = ("description", "category",)

# ------------------------------------------------------------------------------
# 4. Multi-Choice Question Admin
# ------------------------------------------------------------------------------
class MCQuestionAdmin(admin.ModelAdmin): # TranslationAdmin에서 admin.ModelAdmin으로 변경
    list_display = ("content",)
    fieldsets = [
        (None, {'fields': ("content", "explanation", "quiz")}) # 튜플 형식을 깔끔하게 수정
    ]
    search_fields = ("content", "explanation")
    filter_horizontal = ("quiz",)
    inlines = [ChoiceInline]

# ------------------------------------------------------------------------------
# 5. 기타 Admin 등록
# ------------------------------------------------------------------------------
class ProgressAdmin(admin.ModelAdmin):
    search_fields = ("user", "score",)

class EssayQuestionAdmin(admin.ModelAdmin):
    list_display = ("content",)
    fields = ("content", "quiz", "explanation",)
    search_fields = ("content", "explanation")
    filter_horizontal = ("quiz",)

admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(EssayQuestion, EssayQuestionAdmin)
admin.site.register(Sitting)