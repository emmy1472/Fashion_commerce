from django.db import models
from django.conf import settings



class CollaborationRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_collab", on_delete=models.CASCADE)
    reciever = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_collab", on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, 
                              choices=[
                                  ('pending', 'Pending'),
                                  ('accepted', 'Accepted'),
                                  ('rejected', 'Rejected'),
                              ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Collaboration(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="collab_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="collab_user2", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)