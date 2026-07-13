from django.urls import path
from .views import (
    PartnerProfileAPIView,
    PartnerProfileUpdateAPIView,
    PartnerProjectsListAPIView,
)

urlpatterns = [
    path('profile/', PartnerProfileAPIView.as_view()),
    path('profile/update/', PartnerProfileUpdateAPIView.as_view()),
    path('projects/', PartnerProjectsListAPIView.as_view()),
]