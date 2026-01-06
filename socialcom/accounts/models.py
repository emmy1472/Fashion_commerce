from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.utils import timezone
from datetime import timedelta




class User(AbstractUser):
    ROLE_CHOICES = [
        ('model', 'Model'),
        ('designer', 'Designer'),
        ('brand', 'Brand'),
        ('stylist', 'Stylist'),
        ('tailor', 'Tailor')
    ]
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=20)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username still required unless removed

    def __str__(self):
        return f"{self.username} ({self.role})"



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    # Keep db_column mapping for backwards compatibility with older migrations that
    # created a field named 'Profile_image'. Using `db_column` avoids requiring an
    # immediate schema migration to rename the underlying column.
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True, db_column='Profile_image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class EmailVerification(models.Model):
    """One-time email verification code tied to a user.

    The code expires after a short time and is removed after successful
    verification to avoid reuse.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=10)
    

class PasswordResetOTP(models.Model):
    """One-time password reset code for users."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return timezone.now() > self.created_at + timedelta(minutes=10)
    

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        # User has no `name` field; prefer username or email for display
        return f"{self.user.email} -> {self.role.name}"