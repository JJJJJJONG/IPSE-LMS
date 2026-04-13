import os
import shutil
import subprocess
import tempfile

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
@require_POST
def compiler_run(request):
    language = request.POST.get("language", "python")
    code = request.POST.get("code", "").strip()
    stdin = request.POST.get("stdin", "")

    if not code:
        return JsonResponse({"ok": False, "output": "코드를 입력해주세요."}, status=400)

    if language not in ["python", "c", "cpp"]:
        return JsonResponse({"ok": False, "output": "지원하지 않는 언어입니다."}, status=400)

    if language == "c" and shutil.which("gcc") is None:
        return JsonResponse({"ok": False, "output": "gcc가 설치되어 있지 않습니다."}, status=500)

    if language == "cpp" and shutil.which("g++") is None:
        return JsonResponse({"ok": False, "output": "g++가 설치되어 있지 않습니다."}, status=500)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            if language == "python":
                source_path = os.path.join(temp_dir, "main.py")
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(code)

                result = subprocess.run(
                    ["python3", source_path],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3,
                )

            elif language == "c":
                source_path = os.path.join(temp_dir, "main.c")
                binary_path = os.path.join(temp_dir, "main.out")

                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    ["gcc", source_path, "-o", binary_path],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )

                if compile_result.returncode != 0:
                    return JsonResponse(
                        {"ok": False, "output": compile_result.stderr or "C 컴파일 오류가 발생했습니다."},
                        status=400,
                    )

                result = subprocess.run(
                    [binary_path],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3,
                )

            else:
                source_path = os.path.join(temp_dir, "main.cpp")
                binary_path = os.path.join(temp_dir, "main.out")

                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    ["g++", source_path, "-o", binary_path],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )

                if compile_result.returncode != 0:
                    return JsonResponse(
                        {"ok": False, "output": compile_result.stderr or "C++ 컴파일 오류가 발생했습니다."},
                        status=400,
                    )

                result = subprocess.run(
                    [binary_path],
                    input=stdin,
                    text=True,
                    capture_output=True,
                    timeout=3,
                )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n" if output else "") + result.stderr

        if not output.strip():
            output = "출력이 없습니다."

        return JsonResponse({"ok": True, "output": output})

    except subprocess.TimeoutExpired:
        return JsonResponse({"ok": False, "output": "실행 시간이 초과되었습니다."}, status=400)

    except Exception as e:
        return JsonResponse({"ok": False, "output": f"오류가 발생했습니다: {str(e)}"}, status=500)