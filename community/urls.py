from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_main, name='community_main'),
    path('post/add/', views.post_add, name='post_add'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('notice/<int:notice_id>/', views.notice_detail, name='notice_detail'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('upload-image/', views.upload_editor_image, name='upload_editor_image'),
]