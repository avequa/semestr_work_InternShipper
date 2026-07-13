from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from teams.models import Team, TeamMember
from students.models import StudentProfile
from .serializers import TeamSerializer


class MyTeamAPIView(APIView):
    """
    Получение информации о команде студента
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Моя команда", description="Возвращает команду, в которой состоит текущий студент")
    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({"detail": "Вы не студент"}, status=403)

        member = TeamMember.objects.filter(student=student).first()
        if not member:
            return Response({"detail": "Вы не состоите в команде"}, status=404)

        serializer = TeamSerializer(member.team)
        return Response(serializer.data)


class CreateTeamAPIView(APIView):
    """
    Создание новой команды студентом (он будет капитаном)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать команду",
        description="Студент создаёт новую команду и становится её капитаном"
    )
    def post(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({"detail": "Вы не студент"}, status=403)

        if TeamMember.objects.filter(student=student).exists():
            return Response({"detail": "Вы уже состоите в команде"}, status=400)

        name = request.data.get('name')
        description = request.data.get('description')

        team = Team.objects.create(
            name=name,
            description=description,
            captain=student
        )
        TeamMember.objects.create(team=team, student=student)

        return Response({"detail": "Команда создана"})