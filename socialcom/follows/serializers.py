from rest_framework import serializers
from .models import Follow
from accounts.serializers import UserListSerializer

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(source='follower.username', read_only=True)
    following_username = serializers.CharField(source='following.username', read_only=True)
    follower = UserListSerializer(read_only=True)
    following = UserListSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'follower_username', 'following_username', 'created_at']
        read_only_fields = ['id', 'created_at']