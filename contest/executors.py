import os
import subprocess
import tempfile


def execute_code(problem, source_code, input_data, language="python"):
    if language != "python":
        return {
            "success": False,
            "actual_output": "",
            "error_message": "현재는 Python만 지원합니다.",
            "execution_time_ms": None,
            "memory_kb": None,
        }

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "main.py")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(source_code)

        try:
            completed = subprocess.run(
                ["python3", file_path],
                input=input_data,
                text=True,
                capture_output=True,
                timeout=2,
                cwd=temp_dir,
            )

            if completed.returncode != 0:
                return {
                    "success": False,
                    "actual_output": completed.stdout.strip(),
                    "error_message": completed.stderr.strip() or "런타임 에러",
                    "execution_time_ms": None,
                    "memory_kb": None,
                }

            return {
                "success": True,
                "actual_output": completed.stdout.strip(),
                "error_message": "",
                "execution_time_ms": None,
                "memory_kb": None,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "actual_output": "",
                "error_message": "시간 초과",
                "execution_time_ms": None,
                "memory_kb": None,
            }