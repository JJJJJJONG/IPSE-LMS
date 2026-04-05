from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CourseCategory, Course, UserCourseProgress, Upload, UploadVideo

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

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    videos = UploadVideo.objects.filter(course=course)
    files = Upload.objects.filter(course=course)
    progress, created = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
    
    return render(request, 'course/course_detail.html', {
        'course': course,
        'videos': videos,
        'files': files,
        'progress': progress,
    })