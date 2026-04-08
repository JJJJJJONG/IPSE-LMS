from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from .tasks import process_judge_task
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q


from .models import (
    Contest,
    ContestParticipant,
    ContestProblem,
    ContestSubmission,
    JudgeTask,
)


def contest_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all").strip()

    now = timezone.now()

    base_queryset = Contest.objects.filter(is_active=True)

    if q:
        base_queryset = base_queryset.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    contests = list(base_queryset.order_by("-start_time"))

    def get_contest_status(contest):
        if now < contest.start_time:
            return "예정"

        freeze_start = contest.end_time - timezone.timedelta(minutes=contest.freeze_minutes or 0)

        if contest.start_time <= now < freeze_start:
            return "진행 중"

        if freeze_start <= now < contest.end_time:
            return "동결 중"

        return "종료"

    for contest in contests:
        contest.computed_status = get_contest_status(contest)

    if status == "upcoming":
        contests = [contest for contest in contests if contest.computed_status == "예정"]
    elif status == "live":
        contests = [contest for contest in contests if contest.computed_status == "진행 중"]
    elif status == "ended":
        contests = [contest for contest in contests if contest.computed_status == "종료"]

    all_contests = list(Contest.objects.filter(is_active=True).order_by("-start_time"))
    for contest in all_contests:
        contest.computed_status = get_contest_status(contest)

    live_contests = [contest for contest in all_contests if contest.computed_status == "진행 중"]

    live_scoreboards = []

    for live_contest in live_contests:
        contest_problems = live_contest.contest_problems.select_related("problem").order_by("order", "id")

        participant_rows = ContestParticipant.objects.filter(
            contest=live_contest
        ).select_related("user")
        user_map = {participant.user_id: participant.user for participant in participant_rows}

        submission_user_ids = ContestSubmission.objects.filter(
            contest=live_contest
        ).values_list("user_id", flat=True).distinct()

        missing_user_ids = [user_id for user_id in submission_user_ids if user_id not in user_map]

        if missing_user_ids:
            User = get_user_model()
            for user in User.objects.filter(id__in=missing_user_ids):
                user_map[user.id] = user

        users = list(user_map.values())

        scoreboard_rows = []

        for user in users:
            solved_count = 0
            penalty = 0

            for contest_problem in contest_problems:
                submissions = ContestSubmission.objects.filter(
                    contest=live_contest,
                    problem=contest_problem.problem,
                    user=user,
                ).order_by("submitted_at", "id")

                ac_submission = submissions.filter(result="AC").first()

                if ac_submission:
                    solved_count += 1

                    wrong_attempts = submissions.filter(
                        submitted_at__lt=ac_submission.submitted_at
                    ).exclude(result="AC").count()

                    elapsed_minutes = int(
                        (ac_submission.submitted_at - live_contest.start_time).total_seconds() // 60
                    )
                    penalty += elapsed_minutes + (wrong_attempts * 20)

            scoreboard_rows.append(
                {
                    "user": user,
                    "solved_count": solved_count,
                    "penalty": penalty,
                }
            )

        scoreboard_rows.sort(
            key=lambda row: (-row["solved_count"], row["penalty"], str(row["user"]))
        )

        live_scoreboards.append(
            {
                "contest": live_contest,
                "rows": scoreboard_rows[:3],
            }
        )

    return render(
        request,
        "contest/contest_list.html",
        {
            "contests": contests,
            "live_contests": live_contests,
            "live_scoreboards": live_scoreboards,
            "current_q": q,
            "current_status": status,
        },
    )
    
        
def contest_detail(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)
    can_view_problems = can_access_contest_content(request.user, contest)

    contest_problems = []
    if can_view_problems:
        contest_problems = contest.contest_problems.select_related("problem").order_by("order", "id")

    return render(
        request,
        "contest/contest_detail.html",
        {
            "contest": contest,
            "contest_problems": contest_problems,
            "can_view_problems": can_view_problems,
        },
    )


def contest_enter(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)

    if not contest.can_enter():
        return render(
            request,
            "contest/contest_closed.html",
            {
                "contest": contest,
            },
        )

    if request.user.is_authenticated:
        ContestParticipant.objects.get_or_create(
            contest=contest,
            user=request.user,
        )

    contest_problems = contest.contest_problems.select_related("problem").order_by("order", "id")

    problem_rows = []

    for contest_problem in contest_problems:
        status = "-"

        if request.user.is_authenticated:
            submissions = ContestSubmission.objects.filter(
                contest=contest,
                problem=contest_problem.problem,
                user=request.user,
            ).order_by("-submitted_at")

            if submissions.filter(result="AC").exists():
                status = "AC"
            elif submissions.exists():
                status = submissions.first().result

        problem_rows.append(
            {
                "contest_problem": contest_problem,
                "status": status,
            }
        )

    return render(
        request,
        "contest/contest_enter.html",
        {
            "contest": contest,
            "problem_rows": problem_rows,
        },
    )

@login_required
def problem_detail(request, contest_pk, problem_pk):
    contest = get_object_or_404(Contest, pk=contest_pk, is_active=True)

    if not can_access_contest_content(request.user, contest):
        return redirect("contest:detail", pk=contest.pk)

    contest_problem = get_object_or_404(
        ContestProblem,
        contest=contest,
        problem_id=problem_pk,
    )

    submissions = ContestSubmission.objects.filter(
        contest=contest,
        problem=contest_problem.problem,
        user=request.user,
    ).order_by("-submitted_at")

    return render(
        request,
        "contest/problem_detail.html",
        {
            "contest": contest,
            "contest_problem": contest_problem,
            "problem": contest_problem.problem,
            "submissions": submissions,
        },
    )


@login_required
def submit_solution(request, contest_pk, problem_pk):
    contest = get_object_or_404(Contest, pk=contest_pk, is_active=True)

    if not can_access_contest_content(request.user, contest):
        return redirect("contest:detail", pk=contest.pk)

    contest_problem = get_object_or_404(
        ContestProblem,
        contest=contest,
        problem_id=problem_pk,
    )

    if not contest.can_enter():
        return render(
            request,
            "contest/contest_closed.html",
            {
                "contest": contest,
            },
        )

    ContestParticipant.objects.get_or_create(
        contest=contest,
        user=request.user,
    )

    if request.method == "POST":
        language = request.POST.get("language", "python")
        source_code = request.POST.get("source_code", "").strip()

        if source_code:
            submission = ContestSubmission.objects.create(
                contest=contest,
                problem=contest_problem.problem,
                user=request.user,
                language=language,
                source_code=source_code,
                result="PENDING",
                passed_count=0,
                total_count=0,
                judge_message="채점 대기 중입니다.",
            )

            judge_task = JudgeTask.objects.create(
                submission=submission,
                status="QUEUED",
            )

            process_judge_task(judge_task.id)

    return redirect(
        "contest:problem_detail",
        contest_pk=contest.pk,
        problem_pk=contest_problem.problem.pk,
    )

@staff_member_required
def contest_submissions(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)

    submissions = ContestSubmission.objects.filter(
        contest=contest,
    ).select_related("problem", "user", "judge_task").order_by("-submitted_at")

    return render(
        request,
        "contest/submissions.html",
        {
            "contest": contest,
            "submissions": submissions,
        },
    )

@login_required
def my_submissions(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)

    submissions = ContestSubmission.objects.filter(
        contest=contest,
        user=request.user,
    ).select_related("problem", "user", "judge_task").order_by("-submitted_at")

    return render(
        request,
        "contest/my_submissions.html",
        {
            "contest": contest,
            "submissions": submissions,
        },
    )


@login_required
def submission_detail(request, contest_pk, submission_pk):
    contest = get_object_or_404(Contest, pk=contest_pk, is_active=True)
    submission = get_object_or_404(
        ContestSubmission,
        pk=submission_pk,
        contest=contest,
    )

    if not request.user.is_staff and submission.user != request.user:
        return render(
            request,
            "contest/contest_closed.html",
            {
                "contest": contest,
            },
        )

    testcase_results = submission.testcase_results.select_related("testcase").all()
    can_view_full_testcase_results = request.user.is_staff

    return render(
        request,
        "contest/submission_detail.html",
        {
            "contest": contest,
            "submission": submission,
            "testcase_results": testcase_results,
            "can_view_full_testcase_results": can_view_full_testcase_results,
        },
    )

def can_access_contest_content(user, contest):
    if user.is_staff:
        return True
    if not user.is_authenticated:
        return False
    return ContestParticipant.objects.filter(
        contest=contest,
        user=user,
        is_active=True,
    ).exists()


@staff_member_required
def contest_terminate_confirm(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)

    return render(
        request,
        "contest/contest_terminate_confirm.html",
        {
            "contest": contest,
        },
    )


@staff_member_required
@require_POST
def terminate_contest(request, pk):
    contest = get_object_or_404(Contest, pk=pk, is_active=True)

    contest.end_time = timezone.now()
    contest.save(update_fields=["end_time"])

    return redirect("contest:detail", pk=contest.pk)