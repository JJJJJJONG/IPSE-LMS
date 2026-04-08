from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CourseCategory, Course, UserCourseProgress, Upload, UploadVideo, Lesson, CourseComment
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from core.models import ActivityLog
from ranking.utils import sync_user_profile_metrics
import os
import textwrap

@login_required
def course_list(request):
    # 1. 파라미터 가져오기
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    # 2. 기본 쿼리셋
    courses = Course.objects.all()

    # 3. 필터링 적용
    if query:
        courses = courses.filter(title__icontains=query)
    if category_id:
        courses = courses.filter(category_id=category_id)

    categories = CourseCategory.objects.all()
    
    return render(request, 'course/course_list.html', {
        'categories': categories,
        'courses': courses,
        'query': query,
        'selected_category': category_id,
    })

# course/views.py 내부

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    videos = UploadVideo.objects.filter(course=course).order_by('-timestamp')
    files = Upload.objects.filter(course=course)
    progress, created = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
    comments = course.comments.select_related("author").all()

    selected_video = None
    selected_video_id = request.GET.get("video")
    if selected_video_id:
        selected_video = videos.filter(id=selected_video_id).first()
    if not selected_video:
        selected_video = videos.first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "upload_material":
            if not request.user.is_staff:
                return HttpResponseForbidden("업로드 권한이 없습니다.")

            material_file = request.FILES.get("material_file")
            title = request.POST.get("material_title", "").strip()

            if not material_file:
                messages.error(request, "업로드할 실습 자료 파일을 선택해주세요.")
                return redirect("course_detail", slug=course.slug)

            if not title:
                title = os.path.basename(material_file.name)

            Upload.objects.create(course=course, title=title, file=material_file)
            messages.success(request, "실습 자료가 업로드되었습니다.")
            return redirect("course_detail", slug=course.slug)

        if action == "upload_video":
            if not request.user.is_staff:
                return HttpResponseForbidden("업로드 권한이 없습니다.")

            video_file = request.FILES.get("video_file")
            title = request.POST.get("video_title", "").strip()
            summary = request.POST.get("video_summary", "").strip()

            if not video_file:
                messages.error(request, "업로드할 영상 파일을 선택해주세요.")
                return redirect("course_detail", slug=course.slug)

            if not title:
                title = os.path.basename(video_file.name)

            UploadVideo.objects.create(
                course=course,
                title=title,
                summary=summary,
                video=video_file,
            )
            messages.success(request, "영상이 업로드되었습니다.")
            return redirect("course_detail", slug=course.slug)

        if action == "add_comment":
            content = request.POST.get("content", "").strip()
            if not content:
                messages.error(request, "댓글 내용을 입력해주세요.")
                return redirect("course_detail", slug=course.slug)

            CourseComment.objects.create(course=course, author=request.user, content=content)
            return redirect("course_detail", slug=course.slug)

        if action in {"edit_comment", "delete_comment"}:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(CourseComment, id=comment_id, course=course)

            can_edit = request.user == comment.author
            can_delete = request.user == comment.author or (
                request.user.is_staff and not comment.author.is_staff
            )

            if action == "edit_comment":
                if not can_edit:
                    messages.error(request, "댓글 수정 권한이 없습니다.")
                    return redirect("course_detail", slug=course.slug)

                new_content = request.POST.get("content", "").strip()
                if not new_content:
                    messages.error(request, "댓글 내용을 입력해주세요.")
                    return redirect("course_detail", slug=course.slug)

                comment.content = new_content
                comment.save(update_fields=["content"])
                return redirect("course_detail", slug=course.slug)

            if not can_delete:
                messages.error(request, "댓글 삭제 권한이 없습니다.")
                return redirect("course_detail", slug=course.slug)

            comment.delete()
            return redirect("course_detail", slug=course.slug)

    completed_lesson_ids = progress.completed_lessons.values_list('id', flat=True)  
  
    all_lessons = course.lessons.all().order_by('id')
    next_lesson = None
    
    for lesson in all_lessons:
        if lesson.id not in completed_lesson_ids:
            next_lesson = lesson
            break
            
    if not next_lesson and all_lessons.exists():
        next_lesson = all_lessons.first()

    return render(request, 'course/course_detail.html', {
        'course': course,
        'videos': videos,
        'selected_video': selected_video,
        'files': files,
        'progress': progress,
        'comments': comments,
        'completed_lesson_ids': completed_lesson_ids,
        'next_lesson': next_lesson, 
    })

from .models import CourseCategory, Course, UserCourseProgress, Upload, UploadVideo, Lesson

# course/views.py

@login_required
def lesson_detail(request, course_slug, lesson_pk):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    
    # 🚨 [변인 통제 핵심 구역] 
    # 1. 현재 로그인한 유저와 해당 강의의 진행률 객체를 가져옵니다.
    progress, created = UserCourseProgress.objects.get_or_create(
        user=request.user, 
        course=course
    )
    
    # 2. '완료된 레슨 목록'에 현재 레슨이 없다면 추가합니다.
    # ManyToManyField는 .add()를 호출하는 즉시 DB에 반영됩니다.
    lesson_newly_completed = False
    if lesson not in progress.completed_lessons.all():
        progress.completed_lessons.add(lesson)
        lesson_newly_completed = True
        # 확인을 위해 터미널(콘솔)에 로그를 남겨봅니다.
        print(f"DEBUG: {request.user}님이 {lesson.title} 레슨을 완료 처리했습니다.")

    if lesson_newly_completed and progress.progress_percentage == 100:
        ActivityLog.objects.get_or_create(
            user=request.user,
            action_type=ActivityLog.ActionType.COURSE,
            course=course,
            defaults={
                "message": f"{course.title} 강의를 완료했습니다.",
            },
        )

    if lesson_newly_completed:
        sync_user_profile_metrics(request.user)
    
    # 3. 페이징 및 뷰어 렌더링 로직 (기존 유지)
    lessons = list(course.lessons.order_by('id')) 
    current_index = lessons.index(lesson)
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None

    return render(request, 'course/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'total_lessons': len(lessons),
    })

@login_required
def lesson_create(request, course_slug):
    if not request.user.is_staff:
        return redirect('course_detail', slug=course_slug)

    course = get_object_or_404(Course, slug=course_slug)
    # 🚨 units 가져오는 코드 삭제

    if request.method == 'POST':
        # 🚨 unit_id 받는 부분 삭제
        title = request.POST.get('title')
        content = request.POST.get('content') 

        if title and content:
            # 🚨 unit=unit 대신 course=course 로 바로 저장!
            Lesson.objects.create(
                course=course,
                title=title,
                content=content
            )
            return redirect('course_detail', slug=course.slug)

    return render(request, 'course/lesson_create.html', {
        'course': course,
    })

@login_required
@require_POST
def course_update_summary(request, slug):
    """과정 소개글을 실시간으로 업데이트하는 뷰"""
    # 스태프(운영진) 권한 검증
    if not request.user.is_staff:
        return HttpResponseForbidden("편집 권한이 없습니다.")
    
    # 기존 코드의 방식대로 slug를 이용해 Course 객체를 가져옴
    course = get_object_or_404(Course, slug=slug)
    new_summary = request.POST.get('summary')
    
    if new_summary is not None:
        course.summary = textwrap.dedent(new_summary).strip()
        course.save()
        
    return redirect('course_detail', slug=course.slug) 

@login_required
@require_POST
def lesson_delete(request, lesson_pk):
    """커리큘럼(수업)을 삭제하는 뷰"""
    # 스태프 권한 검증
    if not request.user.is_staff:
        return HttpResponseForbidden("삭제 권한이 없습니다.")
        
    # url 파라미터 컨벤션에 맞춰 lesson_pk 사용
    lesson = get_object_or_404(Lesson, pk=lesson_pk)
    
    # 삭제 후 원래 페이지로 돌아가기 위해 slug를 미리 백업해 둠
    course_slug = lesson.course.slug 
    lesson.delete()
    
    return redirect('course_detail', slug=course_slug)
