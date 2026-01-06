from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.ReadOnlyField(source="sender.id")
    sender_email = serializers.ReadOnlyField(source="sender.email")
    sender_username = serializers.ReadOnlyField(source="sender.username")

    class Meta:
        model = Message
        fields = ["id", "sender_id", "sender_username", "sender_email", "text", "timestamp", "is_read"]

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for a conversation. Returns participant metadata and last message."""
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "last_message", "created_at"]

    def get_participants(self, obj):
        return [
            {"id": u.id, "email": u.email, "username": u.username}
            for u in obj.participants.all()
        ]

    def get_last_message(self, obj):
        """Return serialized last message for the conversation (if any)."""
        # support either a method `last_message()` or a property `last_message`
        last = getattr(obj, "last_message", None)
        if callable(last):
            try:
                last = last()
            except Exception:
                last = None
        return MessageSerializer(last).data if last else None