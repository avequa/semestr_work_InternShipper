from django.urls import path
from .views import (
    StudentProfileAPIView,
    StudentProfileUpdateAPIView,
    MyProjectsAPIView,
)

urlpatterns = [
    path("profile/", StudentProfileAPIView.as_view()),
    path("profile/update/", StudentProfileUpdateAPIView.as_view()),
    path("my-projects/", MyProjectsAPIView.as_view()),
]