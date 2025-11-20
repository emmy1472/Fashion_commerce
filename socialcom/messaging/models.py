from django.db import models
from django.conf import settings



User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def last_message(self):
        return self.messages.order_by("-timestamp").first()
    
    def __str__(self):
        return f"Conversation {self.id}"
    

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message by {self.sender} in Conversation {self.conversation.id}"
