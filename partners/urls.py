from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.partner_profile_view, name='partner_profile'),
    path('profile/edit/', views.partner_profile_edit, name='partner_profile_edit'),
    path('profile/delete/', views.partner_profile_delete, name='partner_profile_delete'),

    path('projects/', views.partner_projects, name='partner_projects'),
]
from django.urls import include

urlpatterns += [
    path('api/', include('partners.api.urls')),
]
