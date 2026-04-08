from django.urls import path

from .views import ranking_home

app_name = "ranking"

urlpatterns = [
    path("", ranking_home, name="home"),
]
