from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import NewsAndEvents # 💡 이제 자기 자신의 모델을 가져옴!

@login_required
def community_main(request):
    notices = NewsAndEvents.objects.filter(posted_as='News').order_by('-upload_time')[:5]
    context = {'notices': notices, 'activities': []}
    return render(request, 'community/community_main.html', context)

@staff_member_required
def post_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        posted_as = request.POST.get('posted_as', 'News')
        
        NewsAndEvents.objects.create(title=title, summary=summary, posted_as=posted_as)
        
        referer_url = request.META.get('HTTP_REFERER', 'community_main')
        return redirect(referer_url) 
    return redirect('community_main')

@staff_member_required
def delete_post(request, post_id):
    """공지사항 삭제 뷰"""
    if request.method == 'POST':
        post = get_object_or_404(NewsAndEvents, id=post_id)
        post.delete()
        
        # 💡 삭제 후에는 이전 페이지(Referer)가 아니라 무조건 메인 목록으로 이동!
        return redirect('community_main') 
        
    return redirect('community_main')

@staff_member_required
def edit_post(request, post_id):
    """공지사항 수정 뷰"""
    if request.method == 'POST':
        post = get_object_or_404(NewsAndEvents, id=post_id)
        post.title = request.POST.get('title')
        post.summary = request.POST.get('summary')
        post.save()
        # 💡 수정이 끝나면 다시 그 글의 상세 페이지로 우아하게 이동
        return redirect('notice_detail', notice_id=post.id)
        
    return redirect('community_main')

@login_required
def notice_detail(request, notice_id):
    """공지사항 상세 페이지 뷰"""
    # URL로 전달받은 ID값으로 특정 공지사항 데이터를 찾아옴 (없으면 404 에러)
    notice = get_object_or_404(NewsAndEvents, id=notice_id)
    
    context = {
        'notice': notice
    }
    return render(request, 'community/notice_detail.html', context)