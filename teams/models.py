from django.db import models
from students.models import StudentProfile

class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    captain = models.ForeignKey(
        StudentProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='captain_team'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"название тимы {self.name}"


class TeamMember(models.Model):
    # many to many for team and student profile
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'student')

    def __str__(self):
        return f"{self.student.user.username} in {self.team.name}"