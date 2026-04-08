from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentSignUpForm 
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.core.mail import BadHeaderError
from .models import Student
from .forms import EmailValidationOnForgotPassword


def register(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST) 
        if form.is_valid():
            user = form.save() 
            messages.success(request, "환영합니다! 발급받은 계정으로 로그인해 주세요.")
            return redirect('login') 
        else:
            # 🚨 터미널에 진짜 에러 원인을 출력해 보는 코드 추가!
            print("폼 검증 실패 원인:", form.errors)
            messages.error(request, "입력하신 정보를 다시 확인해 주세요.")
    else:
        form = StudentSignUpForm() 

    return render(request, 'registration/register.html', {'form': form})


class UserPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.txt"
    html_email_template_name = "registration/password_reset_email_html.html"
    subject_template_name = "registration/password_reset_subject.txt"
    form_class = EmailValidationOnForgotPassword
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except (ConnectionError, TimeoutError, OSError, BadHeaderError):
            messages.error(
                self.request,
                "이메일 전송에 실패했습니다. 잠시 후 다시 시도하거나 관리자에게 문의해 주세요.",
            )
            return self.form_invalid(form)

@login_required
@require_POST
def update_profile_api(request):
    """비동기(Fetch API)로 프로필 정보를 업데이트하는 JSON 엔드포인트"""
    try:
        # 1. 프론트엔드에서 보낸 JSON 데이터 파싱
        data = json.loads(request.body)
        
        # 2. 유저와 연결된 Student 객체 가져오기 (없으면 안전하게 생성)
        student, created = Student.objects.get_or_create(student=request.user)
        
        # 3. 데이터 업데이트
        nickname = data.get('nickname', student.nickname).strip()
        if len(nickname) > 30:
            return JsonResponse({"status": "error", "message": "닉네임은 30자 이하로 입력해주세요."}, status=400)

        student.nickname = nickname
        student.bio = data.get('bio', student.bio)
        student.github_url = data.get('github_url', student.github_url)
        student.blog_url = data.get('blog_url', student.blog_url)
        student.save()
        
        # 4. 성공 JSON 응답
        return JsonResponse({"status": "success", "message": "프로필이 업데이트되었습니다."})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

@login_required
@require_POST
def update_profile_picture(request):
    """프로필 이미지를 비동기로 업로드하거나 삭제하는 뷰"""
    user = request.user
    action = request.POST.get('action')

    try:
        if action == 'upload' and 'picture' in request.FILES:
            # 1. 사용자가 이미지를 올린 경우
            user.picture = request.FILES['picture']
            user.save() # models.py에 정의해둔 썸네일 리사이징 로직이 자동 실행됨
            
        elif action == 'delete':
            # 2. X 버튼을 눌러 삭제한 경우 (null로 만들거나 default 이미지로 리셋)
            # models.py에서 default="default.png"로 설정해두었으므로 빈 값을 넣으면 기본 처리됨
            user.picture.delete(save=False) # 기존 물리 파일 삭제 (선택 사항)
            user.picture = "default.png"
            user.save()
            
        # 업데이트된 이미지의 URL을 프론트엔드로 반환하여 화면을 갱신시킴
        return JsonResponse({"status": "success", "image_url": user.get_picture()})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    