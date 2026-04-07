from .judge import run_mock_judge
from .models import JudgeTask


def process_judge_task(judge_task_id):
    judge_task = JudgeTask.objects.select_related("submission").get(id=judge_task_id)
    submission = judge_task.submission
    run_mock_judge(submission)
    return submission