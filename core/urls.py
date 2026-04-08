from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home_view, name="home"),
    path("introduce/", views.introduce_view, name="introduce"),
    path('api/schedules/', views.get_schedules_api, name='get_schedules_api'),
    path('api/schedules/add/', views.add_schedule_api, name='add_schedule_api'),
    path('api/schedules/<int:sch_id>/update/', views.update_schedule_api, name='update_schedule_api'),
    path('api/schedules/<int:sch_id>/delete/', views.delete_schedule_api, name='delete_schedule_api'),
]