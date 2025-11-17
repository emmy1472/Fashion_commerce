from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    if sender.name == "accounts":
        default_roles = [
            "Admin",
            "Brand",
            "Designer",
            "Tailor",
            "stylist",
            "Model",
            "Creator",
            "User"
        ]
        for role in default_roles:
            Role.objects.get_or_create(name=role)