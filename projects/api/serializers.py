from rest_framework import serializers
from projects.models import Project, ProjectApplication


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор для сущности проекта"""

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'requirements',
            'preview',
            'deadline',
            'max_teams',
            'is_active',
            'created_at',
        ]


class ProjectApplicationSerializer(serializers.ModelSerializer):
    """Сериализатор заявки на проект"""

    class Meta:
        model = ProjectApplication
        fields = '__all__'