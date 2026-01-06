from django.db import models
from django.conf import settings


class Opportunity(models.Model):
    CATEGORY_CHOICES = [
        ('photography', 'Photography'),
        ('fashion_design', 'Fashion Design'),
        ('modeling', 'Modeling'),
        ('styling', 'Styling'),
        ('makeup_artistry', 'Makeup Artistry'),
        ('tailoring', 'Tailoring'),
        ('other', 'Other'),
    ]
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=225)
    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


