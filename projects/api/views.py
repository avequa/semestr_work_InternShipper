from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from projects.models import Project, ProjectApplication
from .serializers import ProjectSerializer, ProjectApplicationSerializer


@extend_schema(tags=["Проекты"])
class ProjectListAPIView(generics.ListAPIView):
    """
    Получение списка всех проектов которые активны
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Список проектов",
        description="Возвращает список активных проектов, доступных для записи"
    )
    def get_queryset(self):
        return Project.objects.filter(is_active=True).order_by('-created_at')


@extend_schema(tags=["Проекты"])
class ProjectDetailAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации о проекте.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()


@extend_schema(tags=["Заявки на проекты"])
class ApplyToProjectAPIView(generics.CreateAPIView):
    """
    Подача заявки студентом на проект.
    """
    serializer_class = ProjectApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Подать заявку на проект",
        description="Создаёт заявку текущего студента на выбранный проект."
    )
    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)