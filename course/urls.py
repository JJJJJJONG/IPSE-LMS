from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/lesson/create/', views.lesson_create, name='lesson_create'),
    path('<slug:course_slug>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    
    # 💡 새롭게 추가된 관리자용 API 라우팅
    path('<slug:slug>/update-summary/', views.course_update_summary, name='course_update_summary'),
    path('lesson/<int:lesson_pk>/delete/', views.lesson_delete, name='lesson_delete'),
]