from django.urls import path
from .views import MyTeamAPIView, CreateTeamAPIView

urlpatterns = [
    path('my/', MyTeamAPIView.as_view(), name='api_my_team'),
    path('create/', CreateTeamAPIView.as_view(), name='api_create_team'),
]