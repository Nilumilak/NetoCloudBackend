from django.db import models
import uuid
import os
from storage.models import Storage
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

def get_upload_path(instance, filename):
    return os.path.join(instance.storage.owner.username, *instance.path.split('/'), filename)

class File(models.Model):
    file_data = models.FileField(upload_to=get_upload_path)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=100)
    origin_name = models.CharField(max_length=100)
    url = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=50)
    size = models.PositiveIntegerField()
    path = models.CharField(max_length=300)
    note = models.CharField(max_length=1000, blank=True, default="")
    last_download = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def url_path(self):
        return f"/api/v1/files/{self.url}/"
    
    def __str__(self) -> str:
        return f"{self.name} {self.created_at}"


@receiver(post_save, sender=File)
def file_create(sender, instance, using, **kwargs):
    if kwargs.get("created"):
        storage = instance.storage
        storage.files_count += 1
        storage.files_size += instance.size
        storage.save()


@receiver(post_delete, sender=File)
def file_delete(sender, instance, using, **kwargs):
    storage = instance.storage
    storage.files_count -= 1
    storage.files_size -= instance.size
    storage.save()