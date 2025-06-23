from django.db import models
from django.contrib.auth.models import User
from typing import TYPE_CHECKING

# Create your models here.

if TYPE_CHECKING:
    from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    is_instructor = models.BooleanField(default=False)  # type: ignore
    bio = models.TextField(blank=True, null=True)
    expertise = models.CharField(max_length=200, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {'Instructor' if self.is_instructor else 'Student'}"  # type: ignore
