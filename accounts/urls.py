from django.urls import path
from . import views

# 🚨 에러의 원인이었던 낡은 임포트(LecturerFilterView 등)는 완전히 삭제함!

urlpatterns = [
   
    path("register/", views.register, name="register"),
    path('profile/update/api/', views.update_profile_api, name='update_profile_api'),
    path('profile/picture/update/', views.update_profile_picture, name='update_profile_picture'),
]