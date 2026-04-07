from django.utils import timezone
from .models import JudgeTask, SubmissionTestCaseResult
from .executors import execute_code

def judge_submission(problem, source_code, language="python"):
    testcases = problem.testcases.all().order_by("order", "id")

    testcase_results = []
    passed_count = 0

    for testcase in testcases:
        execution_result = execute_code(
            problem=problem,
            source_code=source_code,
            input_data=testcase.input_data,
            language=language,
        )

        actual_output = execution_result["actual_output"]
        expected_output = testcase.expected_output.strip()

        passed = (
            execution_result["success"]
            and actual_output.strip() == expected_output
        )

        if passed:
            passed_count += 1
            judge_message = "통과"
        else:
            judge_message = execution_result["error_message"] or "출력 불일치"

        testcase_results.append(
            {
                "testcase": testcase,
                "passed": passed,
                "actual_output": actual_output,
                "judge_message": judge_message,
            }
        )

    total_count = len(testcase_results)

    if total_count > 0 and passed_count == total_count:
        judged_result = "AC"
        judge_message = "모든 테스트케이스를 통과했습니다."
    else:
        judged_result = "WA"
        judge_message = "일부 테스트케이스를 통과하지 못했습니다."

    return {
        "result": judged_result,
        "passed_count": passed_count,
        "total_count": total_count,
        "judge_message": judge_message,
        "testcase_results": testcase_results,
    }

def run_mock_judge(submission):
    judge_task = submission.judge_task

    try:
        problem = submission.problem
        source_code = submission.source_code

        judge_task.status = "RUNNING"
        judge_task.started_at = timezone.now()
        judge_task.error_message = ""
        judge_task.save()

        judge_data = judge_submission(problem, source_code, submission.language)

        submission.result = judge_data["result"]
        submission.passed_count = judge_data["passed_count"]
        submission.total_count = judge_data["total_count"]
        submission.judge_message = judge_data["judge_message"]
        submission.save()

        submission.testcase_results.all().delete()

        for testcase_result in judge_data["testcase_results"]:
            SubmissionTestCaseResult.objects.create(
                submission=submission,
                testcase=testcase_result["testcase"],
                passed=testcase_result["passed"],
                actual_output=testcase_result["actual_output"],
                judge_message=testcase_result["judge_message"],
            )

        judge_task.status = "DONE"
        judge_task.finished_at = timezone.now()
        judge_task.save()

        return submission

    except Exception as e:
        submission.result = "RE"
        submission.judge_message = "채점 중 오류가 발생했습니다."
        submission.save()

        judge_task.status = "FAILED"
        judge_task.error_message = str(e)
        judge_task.finished_at = timezone.now()
        judge_task.save()

        return submission