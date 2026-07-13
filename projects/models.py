from django.db import models
from partners.models import PartnerProfile
from teams.models import Team


class Project(models.Model):
    # project from partner
    partner = models.ForeignKey(PartnerProfile, on_delete=models.CASCADE, related_name='projects')

    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    preview = models.ImageField(
        upload_to='projects/previews/',
        null=True,
        blank=True
    )

    deadline = models.DateTimeField()
    max_teams = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"project-name: {self.title}"


class ProjectSubmission(models.Model):
    # project from team
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='submissions')

    file = models.FileField(upload_to='projects/subm/')
    subm_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'team')

    def __str__(self):
        return f"{self.team.name} + {self.project.title}"


class ProjectApplication(models.Model):
    # Статусы заявки. Значение в БД ('pending'/'approved'/'rejected') —
    # то, на что завязаны кнопки и появление чата; справа — текст для интерфейса.
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На рассмотрении'),
        (STATUS_APPROVED, 'Одобрена'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, null=True, blank=True)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)

    # Новое поле. choices даёт метод get_status_display() автоматически.
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'student')

    def __str__(self):
        who = self.team.name if self.team else (self.student.user.username if self.student else '—')
        return f"{who} → {self.project.title} ({self.get_status_display()})"
