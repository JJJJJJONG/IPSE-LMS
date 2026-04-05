# core/urls.py
from django.urls import path
from . import views # views 전체를 가져오는 게 나중에 확장하기 더 편해요.

urlpatterns = [
    # 🏠 메인 대시보드 (로그인 후 첫 화면)
    path("", views.home_view, name="home"),

    # 📢 공지사항 관리 (타임라인에 글을 올리고 수정하는 기능)
    path("post/add/", views.post_add, name="add_item"),
    path("post/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
]