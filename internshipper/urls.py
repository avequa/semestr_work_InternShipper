from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def staff_only(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/?next=' + request.path)

        if not request.user.is_staff:
            return redirect('/')

        return view(request, *args, **kwargs)

    return wrapper


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('students/', include('students.urls')),
    path('partners/', include('partners.urls')),
    path('teams/', include('teams.urls')),
    path('accounts/', include('allauth.urls')),
    path('chat/', include('chat.urls')),
    path(
        'api/schema/',
        staff_only(SpectacularAPIView.as_view()),
        name='schema'
    ),
    path(
        'api/swagger/',
        staff_only(
            SpectacularSwaggerView.as_view(url_name='schema')
        ),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        staff_only(
            SpectacularRedocView.as_view(url_name='schema')
        ),
        name='redoc',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)