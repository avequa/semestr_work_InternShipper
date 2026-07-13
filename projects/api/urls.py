from django.urls import path
from .views import (
    ProjectListAPIView,
    ProjectDetailAPIView,
    ApplyToProjectAPIView,
)

urlpatterns = [
    path('list/', ProjectListAPIView.as_view()),
    path('<int:pk>/', ProjectDetailAPIView.as_view()),
    path('<int:pk>/apply/', ApplyToProjectAPIView.as_view()),
]