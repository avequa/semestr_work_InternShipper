from django.db import models
from django.contrib.auth.models import User

class PartnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='partner_logos/', null=True, blank=True)
    def __str__(self):
        return f"company name: {self.company_name} + company fullname: {self.user.get_full_name()}"
