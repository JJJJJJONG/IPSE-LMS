from collections import defaultdict

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from contest.models import Contest, ContestParticipant, ContestSubmission
from course.models import UserCourseProgress
from problems.models import SolveRecord


LESSON_XP = 10
XP_PER_LEVEL = 100


def calculate_level_from_xp(learning_xp):
    xp = max(int(learning_xp or 0), 0)
    return (xp // XP_PER_LEVEL) + 1


def get_learning_xp_map(user_ids=None):
    progress_qs = UserCourseProgress.objects.values("user_id").annotate(
        completed_lessons=Count("completed_lessons", distinct=True)
    )

    if user_ids is not None:
        progress_qs = progress_qs.filter(user_id__in=user_ids)

    return {
        row["user_id"]: (row["completed_lessons"] or 0) * LESSON_XP
        for row in progress_qs
    }


def get_problem_points_map(user_ids=None):
    solved_qs = SolveRecord.objects.filter(status="SOLVED").values("user_id").annotate(
        points=Sum("problem__points")
    )

    if user_ids is not None:
        solved_qs = solved_qs.filter(user_id__in=user_ids)

    return {row["user_id"]: row["points"] or 0 for row in solved_qs}


def get_contest_wins_map(user_ids=None):
    finished_contests = list(
        Contest.objects.filter(is_active=True, end_time__lte=timezone.now()).values(
            "id", "start_time"
        )
    )
    if not finished_contests:
        return {}

    contest_ids = [contest["id"] for contest in finished_contests]
    contest_start_map = {contest["id"]: contest["start_time"] for contest in finished_contests}

    contest_user_scores = defaultdict(dict)

    for row in ContestParticipant.objects.filter(contest_id__in=contest_ids).values(
        "contest_id", "user_id"
    ):
        contest_user_scores[row["contest_id"]].setdefault(
            row["user_id"],
            {"solved_count": 0, "penalty": 0},
        )

    problem_tracker = {}
    submissions = ContestSubmission.objects.filter(contest_id__in=contest_ids).values(
        "contest_id",
        "user_id",
        "problem_id",
        "result",
        "submitted_at",
    ).order_by("contest_id", "user_id", "problem_id", "submitted_at", "id")

    for submission in submissions:
        contest_id = submission["contest_id"]
        user_id = submission["user_id"]
        problem_id = submission["problem_id"]
        result = submission["result"]

        contest_user_scores[contest_id].setdefault(
            user_id,
            {"solved_count": 0, "penalty": 0},
        )

        tracker_key = (contest_id, user_id, problem_id)
        tracker = problem_tracker.setdefault(
            tracker_key,
            {"solved": False, "wrong_attempts": 0},
        )

        if tracker["solved"]:
            continue

        if result == "AC":
            tracker["solved"] = True
            elapsed_minutes = int(
                (submission["submitted_at"] - contest_start_map[contest_id]).total_seconds() // 60
            )

            contest_user_scores[contest_id][user_id]["solved_count"] += 1
            contest_user_scores[contest_id][user_id]["penalty"] += (
                elapsed_minutes + tracker["wrong_attempts"] * 20
            )
        elif result != "PENDING":
            tracker["wrong_attempts"] += 1

    all_user_ids = set()
    for user_scores in contest_user_scores.values():
        all_user_ids.update(user_scores.keys())

    User = get_user_model()
    username_map = {
        user.id: user.username.lower()
        for user in User.objects.filter(id__in=all_user_ids).only("id", "username")
    }

    filter_ids = set(user_ids) if user_ids is not None else None
    wins_by_user = defaultdict(int)

    for user_scores in contest_user_scores.values():
        if not user_scores:
            continue

        winner_id = sorted(
            user_scores.keys(),
            key=lambda uid: (
                -user_scores[uid]["solved_count"],
                user_scores[uid]["penalty"],
                username_map.get(uid, ""),
            ),
        )[0]

        if filter_ids is not None and winner_id not in filter_ids:
            continue

        wins_by_user[winner_id] += 1

    return dict(wins_by_user)


def get_user_metrics(user):
    user_id = user.id
    learning_xp = get_learning_xp_map([user_id]).get(user_id, 0)
    problem_points = get_problem_points_map([user_id]).get(user_id, 0)
    contest_wins = get_contest_wins_map([user_id]).get(user_id, 0)
    level = calculate_level_from_xp(learning_xp)

    return {
        "learning_xp": learning_xp,
        "level": level,
        "problem_points": problem_points,
        "contest_wins": contest_wins,
    }


def sync_user_profile_metrics(user):
    metrics = get_user_metrics(user)

    if user.total_points != metrics["problem_points"]:
        user.total_points = metrics["problem_points"]
        user.save(update_fields=["total_points"])

    if hasattr(user, "student") and user.student.level != metrics["level"]:
        user.student.level = metrics["level"]
        user.student.save(update_fields=["level"])

    return metrics