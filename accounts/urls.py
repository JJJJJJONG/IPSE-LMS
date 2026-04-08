from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

# 🚨 에러의 원인이었던 낡은 임포트(LecturerFilterView 등)는 완전히 삭제함!

urlpatterns = [
    path(
        "password_reset/",
        views.UserPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("register/", views.register, name="register"),
    path('profile/update/api/', views.update_profile_api, name='update_profile_api'),
    path('profile/picture/update/', views.update_profile_picture, name='update_profile_picture'),
]