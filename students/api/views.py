from rest_framework.generics import RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from students.models import StudentProfile
from projects.models import ProjectApplication
from teams.models import TeamMember

from .serializers import (
    StudentProfileSerializer,
    MyProjectApplicationSerializer,
)


@extend_schema(
    summary="Профиль студента",
    description="Возвращает данные профиля текущего авторизованного студента",
)
class StudentProfileAPIView(RetrieveAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.student_profile


@extend_schema(
    summary="Редактирование профиля",
    description="Изменение профиля студентом",)
class StudentProfileUpdateAPIView(UpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.student_profile


@extend_schema(
    summary="Мои проекты",
    description="Список всех заявок студента на проекты: личных и командных",)
class MyProjectsAPIView(ListAPIView):
    serializer_class = MyProjectApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student = self.request.user.student_profile

        solo = ProjectApplication.objects.filter(student=student)

        team_member = TeamMember.objects.filter(student=student).first()
        if team_member:
            team = ProjectApplication.objects.filter(team=team_member.team)
        else:
            team = ProjectApplication.objects.none()

        return (solo | team).select_related(
            "project", "project__partner", "team"
        ).distinct().order_by("-applied_at")