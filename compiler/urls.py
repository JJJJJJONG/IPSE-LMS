from django.urls import path
from .views import compiler_run

urlpatterns = [
    path("run/", compiler_run, name="compiler_run"),
]