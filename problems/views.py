# problems/views.py

from django.shortcuts import render
from .models import Problem, SolveRecord
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from course.models import CourseCategory
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

User = get_user_model()

def problem_list(request):
    # 1. 풀이 수(solve_count)를 계산해서 한 번에 가져오기 (124 버그 해결)
    # SolveRecord 중 상태가 'SOLVED'인 것만 카운트함
    problems = Problem.objects.select_related('category', 'author').annotate(
        solve_count=Count('solverecord', filter=Q(solverecord__status='SOLVED'))
    )
    
    categories = CourseCategory.objects.all()

    # 2. 파라미터 가져오기
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q', '').strip() # 검색어 공백 제거
    sort_by = request.GET.get('sort', 'newest') # 기본값은 최신순

    # 3. 필터링 및 검색 적용 (검색 기능 정상화)
    if category_id:
        problems = problems.filter(category_id=category_id)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if search_query:
        problems = problems.filter(title__icontains=search_query)

    # 4. 정렬 로직 적용
    if sort_by == 'most_solved':
        problems = problems.order_by('-solve_count', '-created_at')
    elif sort_by == 'least_solved':
        problems = problems.order_by('solve_count', '-created_at')
    else: # newest
        problems = problems.order_by('-created_at')

    top_rankers = User.objects.order_by('-total_points')[:10]

    user_status = {}
    if request.user.is_authenticated:
        records = SolveRecord.objects.filter(user=request.user)
        user_status = {r.problem_id: r.status for r in records}

    context = {
        'problems': problems,
        'categories': categories,
        'top_rankers': top_rankers,
        'user_status': user_status,
        'current_category': category_id,
        'current_difficulty': difficulty,
        'current_q': search_query,
        'current_sort': sort_by,
    }
    return render(request, 'problems/problem_list.html', context)

def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    
    # 1. 파일과 댓글 가져오기 (related_name 활용)
    attachments = problem.attachments.all()
    comments = problem.comments.all().order_by('-created_at')
    
    # 2. 풀이자 정보 (First Blood 및 최근 풀이자)
    solvers = SolveRecord.objects.filter(problem=problem, status='SOLVED').select_related('user').order_by('solved_at')
    first_blood = solvers.first() # 가장 먼저 푼 사람
    recent_solvers = solvers.order_by('-solved_at')[:5] # 최근 5명
    
    # 3. 플래그(Flag) 제출 처리 로직
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "로그인이 필요합니다.")
            return redirect('login')
            
        submitted_flag = request.POST.get('flag', '').strip()
        
        # 정답일 경우
        if submitted_flag == problem.flag:
            record, created = SolveRecord.objects.get_or_create(user=request.user, problem=problem)
            if record.status != 'SOLVED':
                record.status = 'SOLVED'
                record.solved_at = timezone.now()
                record.save()
                messages.success(request, f"🎉 정답입니다! {problem.points} 포인트를 획득했습니다.")
            else:
                messages.info(request, "이미 풀이한 문제입니다.")
        # 오답일 경우
        else:
            messages.error(request, "❌ 플래그가 틀렸습니다. 다시 시도해 보세요!")
            
        return redirect('problem_detail', pk=pk)

    context = {
        'problem': problem,
        'attachments': attachments,
        'comments': comments,
        'first_blood': first_blood,
        'recent_solvers': recent_solvers,
        'solvers_count': solvers.count(),
    }
    return render(request, 'problems/problem_detail.html', context)