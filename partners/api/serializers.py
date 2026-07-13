from rest_framework import serializers
from partners.models import PartnerProfile
from projects.models import Project


class PartnerProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для сущности профиля партнера"""

    class Meta:
        model = PartnerProfile
        fields = [
            'company_name',
            'position',
            'website',
            'phone',
            'logo',
            'is_verified',
        ]


class PartnerProjectSerializer(serializers.ModelSerializer):
    """Сериализатор для проектов, созданных партнером"""

    class Meta:
        model = Project
        fields = '__all__'