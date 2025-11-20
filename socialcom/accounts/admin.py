from django.contrib import admin
from .models import User, Profile, UserRole, Role, EmailVerification, PasswordResetOTP

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(UserRole)
admin.site.register(Role)
admin.site.register(EmailVerification)
admin.site.register(PasswordResetOTP)
