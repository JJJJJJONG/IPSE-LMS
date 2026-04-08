from django.urls import path

from .views import (
    contest_detail,
    contest_enter,
    contest_list,
    contest_submissions,
    contest_terminate_confirm,
    my_submissions,
    problem_detail,
    submission_detail,
    submit_solution,
    terminate_contest,
)

app_name = "contest"

urlpatterns = [
    path("", contest_list, name="list"),
    path("<int:pk>/", contest_detail, name="detail"),
    path("<int:pk>/enter/", contest_enter, name="enter"),
    path("<int:pk>/my-submissions/", my_submissions, name="my_submissions"),
    path("<int:pk>/submissions/", contest_submissions, name="submissions"),
    path("<int:pk>/terminate/confirm/", contest_terminate_confirm, name="terminate_confirm"),
    path("<int:pk>/terminate/", terminate_contest, name="terminate"),
    path(
        "<int:contest_pk>/problems/<int:problem_pk>/",
        problem_detail,
        name="problem_detail",
    ),
    path(
        "<int:contest_pk>/problems/<int:problem_pk>/submit/",
        submit_solution,
        name="submit_solution",
    ),
    path(
        "<int:contest_pk>/submissions/<int:submission_pk>/",
        submission_detail,
        name="submission_detail",
    ),
]