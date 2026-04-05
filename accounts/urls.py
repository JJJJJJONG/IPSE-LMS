from django.urls import path
from . import views

# 🚨 에러의 원인이었던 낡은 임포트(LecturerFilterView 등)는 완전히 삭제함!

urlpatterns = [
    # 🔐 인증 관련 (우리가 방금 살려낸 핵심 기능들)
    path("register/", views.register, name="register"),
    #path("login/validate_username/", views.validate_username, name="validate_username"),
    
    # 👤 프로필 및 설정
    #path("profile/", views.profile, name="profile"),
    #path("profile/update/", views.profile_update, name="profile_update"),
    #path("password-change/", views.change_password, name="change_password"),
    
    # 운영진/동아리원 관리 등 낡은 경로는 모두 삭제 완료!
]