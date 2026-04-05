from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import StudentSignUpForm  # 🚨 하이브리드 폼으로 교체 완료!

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

    