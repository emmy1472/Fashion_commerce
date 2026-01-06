from django.contrib import admin
from .models import User, Profile, UserRole, Role, EmailVerification, PasswordResetOTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('email', 'username', 'is_verified', 'is_active')
	search_fields = ('email', 'username')
	list_filter = ('is_verified', 'is_active', 'role')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'full_name', 'location', 'created_at')
	search_fields = ('user__email', 'full_name')


admin.site.register(UserRole)
admin.site.register(Role)
admin.site.register(EmailVerification)
admin.site.register(PasswordResetOTP)
