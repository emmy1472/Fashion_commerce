from django.contrib import admin
from .models import Post, Like, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'caption', 'created_at')
	search_fields = ('user__email', 'caption', 'tags')
	list_filter = ('created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'post', 'created_at')
	search_fields = ('user__email',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'post', 'created_at')
	search_fields = ('user__email', 'content')
