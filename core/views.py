from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from community.models import NewsAndEvents
from .models import ActivityLog, Schedule 
from ranking.utils import sync_user_profile_metrics


def introduce_view(request):
    """소개 페이지 렌더링"""
    return render(request, "introduce.html")


# ########################################################
# 1. IPSE 메인 대시보드 (Traffic Controller)
# ########################################################
@login_required
def home_view(request):
    """유저의 로그인 상태를 확인하고 대시보드에 필요한 모든 데이터를 공급함"""
    
    # 1. 오른쪽 위 공지사항 (News)
    notices = NewsAndEvents.objects.filter(posted_as='News').order_by('-upload_time')[:5]
    
    # 2. 왼쪽 아래 달력용 데이터 (Event)
    events = NewsAndEvents.objects.filter(posted_as='Event').order_by('-upload_time')[:5]
    
    # 3. 오른쪽 아래 활동 내역 (해당 유저의 활동만)
    activity_logs = ActivityLog.objects.filter(user=request.user)[:10]
    metrics = sync_user_profile_metrics(request.user)

    context = {
        'notices': notices,
        'events': events,
        'activity_logs': activity_logs,
        'learning_level': metrics['level'],
        'problem_points': metrics['problem_points'],
        'contest_wins': metrics['contest_wins'],
        'title': 'IPSE AI Academy 대시보드'
    }
    return render(request, 'core/index.html', context)

# ... (이 아래 get_schedules_api 등 달력 로직은 기존 코드 100% 그대로 유지!) ...

@login_required
def get_schedules_api(request):
    """달력에 표시할 일정들을 JSON으로 반환하는 API"""
    # 핵심 필터링 로직: '전체 동아리 일정(is_global=True)' 이거나 '내가 작성한 일정(user=request.user)'만 가져옴
    schedules = Schedule.objects.filter(Q(is_global=True) | Q(user=request.user))
    
    events = []
    for s in schedules:
        events.append({
            'id': s.id,
            'title': s.title,
            'start': s.start_date.isoformat(),
            'end': s.end_date.isoformat() if s.end_date else None,
            'color': '#10b981' if s.is_global else '#a855f7', 
            'extendedProps': {
                'description': s.description,
                'is_global': s.is_global
            }
        })
    return JsonResponse(events, safe=False)

@login_required
@require_POST
def add_schedule_api(request):
    """새로운 일정을 데이터베이스에 저장하는 API"""
    try:
        data = json.loads(request.body)
        is_global = data.get('is_global', False)

        # 💡 보안 검증: 일반 유저가 악의적으로 전체 일정을 만들려고 하면 강제로 개인 일정으로 변경
        if not request.user.is_staff:
            is_global = False

        Schedule.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            start_date=data.get('start'),
            end_date=data.get('end'),
            user=request.user,
            is_global=is_global
        )
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
@require_POST
def delete_schedule_api(request, sch_id):
    """일정을 삭제하는 API"""
    try:
        schedule = get_object_or_404(Schedule, id=sch_id)
        
        if schedule.user != request.user and not request.user.is_staff:
            return JsonResponse({"status": "error", "message": "권한이 없습니다."}, status=403)

        schedule.delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
@require_POST
def update_schedule_api(request, sch_id):
    """기존 일정을 수정하는 API"""
    try:
        schedule = get_object_or_404(Schedule, id=sch_id)
        
        # 권한 체크: 내가 쓴 글이거나 관리자(staff)여야만 수정 가능
        if schedule.user != request.user and not request.user.is_staff:
            return JsonResponse({"status": "error", "message": "권한이 없습니다."}, status=403)

        data = json.loads(request.body)
        schedule.title = data.get('title', schedule.title)
        schedule.description = data.get('description', schedule.description)
        schedule.start_date = data.get('start', schedule.start_date)
        schedule.end_date = data.get('end', schedule.end_date)
        
        if request.user.is_staff:
            schedule.is_global = data.get('is_global', schedule.is_global)

        schedule.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
        


