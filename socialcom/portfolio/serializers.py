from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'image', 'tags', 'created_at', 'updated_at']

        def create(self, validated_data):
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)