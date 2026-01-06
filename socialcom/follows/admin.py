from django.contrib import admin
from .models import Follow

# Register your models here.
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
	list_display = ('id', 'follower', 'following', 'created_at')
	search_fields = ('follower__email', 'following__email')
	list_filter = ('created_at',)
