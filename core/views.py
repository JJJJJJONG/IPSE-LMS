from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# IPSE 전용 데코레이터와 모델, 폼 임포트
from accounts.decorators import lecturer_required 
from .forms import NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog

# ########################################################
# 1. IPSE 메인 관문 (Traffic Controller)
# ########################################################
def home_view(request):
    """유저의 로그인 상태를 확인하고 올바른 목적지로 안내함"""
    if not request.user.is_authenticated:
        # 로그인을 안 했다면 로그인 창으로 튕겨냄
        return redirect('login')

    # 최신 데이터 추출 (대시보드용)
    news_items = NewsAndEvents.objects.all().order_by('-upload_time')[:3]
    activity_logs = ActivityLog.objects.all().order_by('-created_at')[:5]

    context = {
        'news_items': news_items,
        'activity_logs': activity_logs,
        'title': 'IPSE AI Academy 대시보드'
    }
    return render(request, 'core/index.html', context)


# ########################################################
# 2. IPSE 동아리 공지사항 (운영 로직)
# ########################################################
@login_required
@lecturer_required # 부회장님 같은 운영진만 글을 쓸 수 있게 제한합니다.
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "새로운 소식이 타임라인에 등록되었습니다.")
            return redirect("home")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"form": form, "title": "소식 등록"})

@login_required
@lecturer_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "소식이 성공적으로 수정되었습니다.")
            return redirect("home")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"form": form, "title": "소식 수정"})

@login_required
@lecturer_required
def delete_post(request, pk):
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post.delete()
    messages.success(request, "소식이 삭제되었습니다.")
    return redirect("home")