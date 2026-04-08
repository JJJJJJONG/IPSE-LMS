from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ranking.utils import sync_user_profile_metrics
from course.models import CourseCategory
from core.models import ActivityLog
from .models import Problem, ProblemComment, SolveRecord

User = get_user_model()


def problem_list(request):
    problems = Problem.objects.select_related("category", "author").annotate(
        solve_count=Count("solverecord", filter=Q(solverecord__status="SOLVED"))
    )

    categories = CourseCategory.objects.all()

    category_id = request.GET.get("category")
    difficulty = request.GET.get("difficulty")
    search_query = request.GET.get("q", "").strip()
    sort_by = request.GET.get("sort", "newest")

    if category_id:
        problems = problems.filter(category_id=category_id)
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    if search_query:
        problems = problems.filter(title__icontains=search_query)

    if sort_by == "most_solved":
        problems = problems.order_by("-solve_count", "-created_at")
    elif sort_by == "least_solved":
        problems = problems.order_by("solve_count", "-created_at")
    else:
        problems = problems.order_by("-created_at")

    top_rankers = (
        User.objects.select_related("student").annotate(
            problem_score=Sum(
                'solve_records__problem__points',
                filter=Q(solve_records__status='SOLVED')
            )
        )
        .order_by('-problem_score', 'username')[:10]
    )

    for ranker in top_rankers:
        ranker.problem_score = ranker.problem_score or 0

    user_status = {}
    if request.user.is_authenticated:
        records = SolveRecord.objects.filter(user=request.user)
        user_status = {r.problem_id: r.status for r in records}

    for problem in problems:
        problem.is_solved = user_status.get(problem.id) == "SOLVED"
    context = {
        "problems": problems,
        "categories": categories,
        "top_rankers": top_rankers,
        "user_status": user_status,
        "current_category": category_id,
        "current_difficulty": difficulty,
        "current_q": search_query,
        "current_sort": sort_by,
    }
    return render(request, "problems/problem_list.html", context)


def problem_detail(request, pk):
    problem = get_object_or_404(
        Problem.objects.select_related("author", "author__student", "category"),
        pk=pk,
    )

    comments = problem.comments.select_related("author").all()

    solved_records = (
        SolveRecord.objects.filter(problem=problem, status="SOLVED")
        .select_related("user")
        .order_by("solved_at")
    )

    first_blood = solved_records.first()
    recent_solvers = solved_records.order_by("-solved_at")[:5]

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "로그인이 필요합니다.")
            return redirect("login")

        action = request.POST.get("action")

        if action == "update_description":
            if not request.user.is_staff:
                messages.error(request, "문제 설명 수정 권한이 없습니다.")
                return redirect("problem_detail", pk=pk)

            description = request.POST.get("description", "").strip()
            if not description:
                messages.error(request, "문제 설명을 입력해주세요.")
                return redirect("problem_detail", pk=pk)

            problem.description = description
            problem.save(update_fields=["description"])
            messages.success(request, "문제 설명이 수정되었습니다.")
            return redirect("problem_detail", pk=pk)

        if action == "submit_flag":
            submitted_flag = request.POST.get("flag", "").strip()

            if not submitted_flag:
                messages.error(request, "정답을 입력해주세요.")
                return redirect("problem_detail", pk=pk)

            record, _ = SolveRecord.objects.get_or_create(
                user=request.user,
                problem=problem,
            )

            if submitted_flag == problem.flag:
                if record.status != "SOLVED":
                    record.status = "SOLVED"
                    record.solved_at = timezone.now()
                    record.save()
                    sync_user_profile_metrics(request.user)
                    ActivityLog.objects.get_or_create(
                        user=request.user,
                        action_type=ActivityLog.ActionType.PROBLEM,
                        problem=problem,
                        defaults={
                            "message": f"{problem.title} 문제를 해결했습니다.",
                        },
                    )

                    messages.success(
                        request,
                        f"🎉 정답입니다! {problem.points} 포인트를 획득했습니다.",
                    )
                else:
                    messages.info(request, "이미 해결한 문제입니다.")
            else:
                if record.status == "TODO":
                    record.status = "ATTEMPT"
                    record.save(update_fields=["status"])
                messages.error(request, "❌ 정답이 틀렸습니다. 다시 시도해보세요.")

            return redirect("problem_detail", pk=pk)

        if action == "add_comment":
            content = request.POST.get("content", "").strip()

            if not content:
                messages.error(request, "댓글 내용을 입력해주세요.")
                return redirect("problem_detail", pk=pk)

            ProblemComment.objects.create(
                problem=problem,
                author=request.user,
                content=content,
            )
            return redirect("problem_detail", pk=pk)

        if action in {"edit_comment", "delete_comment"}:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(ProblemComment, id=comment_id, problem=problem)

            can_edit = request.user == comment.author
            can_delete = request.user == comment.author or (
                request.user.is_staff and not comment.author.is_staff
            )

            if action == "edit_comment":
                if not can_edit:
                    messages.error(request, "댓글 수정 권한이 없습니다.")
                    return redirect("problem_detail", pk=pk)

                new_content = request.POST.get("content", "").strip()
                if not new_content:
                    messages.error(request, "댓글 내용을 입력해주세요.")
                    return redirect("problem_detail", pk=pk)

                comment.content = new_content
                comment.save(update_fields=["content"])
                return redirect("problem_detail", pk=pk)

            if not can_delete:
                messages.error(request, "댓글 삭제 권한이 없습니다.")
                return redirect("problem_detail", pk=pk)

            comment.delete()
            return redirect("problem_detail", pk=pk)

    context = {
        "problem": problem,
        "comments": comments,
        "first_blood": first_blood,
        "recent_solvers": recent_solvers,
        "solvers_count": solved_records.count(),
    }
    return render(request, "problems/problem_detail.html", context)