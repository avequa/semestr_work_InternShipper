from rest_framework import serializers
from students.models import StudentProfile
from projects.models import ProjectApplication


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"
        read_only_fields = ("user",)


class MyProjectApplicationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title")
    partner_name = serializers.CharField(source="project.partner.company_name")
    team_name = serializers.CharField(source="team.name", default=None)

    class Meta:
        model = ProjectApplication
        fields = (
            "id",
            "project_title",
            "partner_name",
            "team_name",
            "applied_at",
        )