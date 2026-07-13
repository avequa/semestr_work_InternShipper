from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from students.models import StudentProfile

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if not StudentProfile.objects.filter(user=user).exists():
            StudentProfile.objects.create(user=user)
        return user