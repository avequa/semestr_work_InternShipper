from rest_framework import generics, permissions
from partners.models import PartnerProfile
from projects.models import Project
from .serializers import PartnerProfileSerializer, PartnerProjectSerializer


class PartnerProfileAPIView(generics.RetrieveAPIView):
    """Возврат авторизированного профиля партнера"""
    serializer_class = PartnerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.partner_profile


class PartnerProfileUpdateAPIView(generics.UpdateAPIView):
    """Изменение авторизированного профиля партнера"""
    serializer_class = PartnerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.partner_profile


class PartnerProjectsListAPIView(generics.ListAPIView):
    """Возврат списка проектов авторизированного профиля партнера"""
    serializer_class = PartnerProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            partner=self.request.user.partner_profile
        ).order_by('-created_at')