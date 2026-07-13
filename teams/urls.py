from django.urls import path, include
from . import views

app_name = 'teams'

urlpatterns = [
    path('my-team/', views.my_team, name='my_team'),
    path('create/', views.create_team, name='create_team'),
    path('<int:team_id>/add/', views.add_member, name='add_member'),
    path('<int:team_id>/search/', views.search_students, name='search_students'),
    path('<int:team_id>/invite/<int:student_id>/', views.invite_member, name='invite_member'),
    path('<int:team_id>/remove/<int:member_id>/', views.remove_member, name='remove_member'),
    path('<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('<int:team_id>/delete/', views.delete_team, name='delete_team'),
    path('api/', include('teams.api.urls')),
]