from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(source="sender.email")

    class Meta:
        model = Message
        fields = ["id", "sender_email", "text", "timestamp", "is_read"]

class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "last_message"]

        def get_last_message(self, obj):
            last = obj.last_message()
            return MessageSerializer(last).data if last else None