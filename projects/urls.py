from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.project_create, name = 'project_create'),
    path('list/', views.project_list, name='project_list'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('apply/<int:pk>/', views.apply_to_project, name='apply_to_project'),
    path('<int:pk>/applications/', views.project_applications, name='project_applications'),
    path('<int:project_pk>/applications/<int:application_pk>/update/', views.update_application_status, name='update_application_status'),

    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/add/<int:pk>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:pk>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/toggle/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
]

from django.urls import include

urlpatterns += [
    path('api/', include('projects.api.urls')),
]