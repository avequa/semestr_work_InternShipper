from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:application_id>/', views.open_chat, name='open_chat'),
]
