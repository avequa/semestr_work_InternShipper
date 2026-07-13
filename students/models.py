from django.db import models
from django.contrib.auth.models import User

# id , username , email , password ,
# first_name , last_name , is_active , is_staff , is_superuser
# import User Django Model
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = "student_profile") # профиль сносим вместе с юзером
    uni = models.CharField(max_length=255, blank=True) # для строковых полей не разрешать null
    course = models.IntegerField(null=True, blank=True) # для числовых полей null разрешаем
    speciality = models.CharField(max_length=255, blank=True)
    info = models.TextField(blank=True)
    ava = models.ImageField(upload_to='avatars/', null=True, blank=True)  # для файловых полей null разрешаем
    def __str__(self):
        return f"username: {self.user.username} + student fullname:{self.user.get_full_name()}"

