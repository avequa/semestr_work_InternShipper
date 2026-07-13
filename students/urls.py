from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('my-projects/', views.my_projects, name='my_projects'),
    path('profile/', views.profile_view, name='student_profile'),
    path('profile/edit/', views.profile_edit, name='student_profile_edit'),
    path('profile/delete/', views.profile_delete, name='student_profile_delete'),
    path("api/", include("students.api.urls")),
    path('profile/<int:pk>/', views.student_public_profile, name='student_public_profile'),
]