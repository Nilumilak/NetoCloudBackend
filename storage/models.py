from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Storage(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='storage')
    files_count = models.PositiveIntegerField(default=0)
    files_size = models.PositiveIntegerField(default=0)
    
    def __str__(self) -> str:
        return self.pk


@receiver(post_save, sender=User)
def user_create(sender, instance, using, **kwargs):
    if kwargs.get("created"):
        Storage.objects.create(owner=instance)
