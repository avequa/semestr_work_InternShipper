from django.db import models
from partners.models import PartnerProfile
from projects.models import ProjectSubmission


class Feedback(models.Model):
    # feedback from partners
    submission = models.OneToOneField(ProjectSubmission, on_delete=models.CASCADE, related_name='feedback')

    partner = models.ForeignKey(PartnerProfile, on_delete=models.CASCADE)

    comment = models.TextField()

    is_accepted = models.BooleanField(default=False)
    invite_to_interview = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"feedback for {self.submission}"