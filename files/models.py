import os
import uuid

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from storage.models import Storage


def get_upload_path(instance, filename):
    """
    Returns path for uploading file
    """
    return os.path.join(instance.storage.owner.username, *instance.path.split("/"), filename)


class File(models.Model):
    file_data = models.FileField(upload_to=get_upload_path)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, related_name="files")
    name = models.CharField(max_length=100)
    origin_name = models.CharField(max_length=100)
    url = models.UUIDField(default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=50)
    size = models.PositiveIntegerField()
    path = models.CharField(max_length=300, default="")
    note = models.CharField(max_length=1000, blank=True, default="")
    last_download = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def url_path(self):
        """
        Returns url_path for file download
        """
        return f"/api/v1/files/{self.url}/"

    def __str__(self) -> str:
        """
        File text representation
        """
        return f"{self.name} {self.created_at}"


@receiver(post_save, sender=File)
def file_create(sender, instance, using, **kwargs):
    """
    Increments storage file_count and file_size after File was uploaded
    """
    if kwargs.get("created"):
        storage = instance.storage
        storage.files_count += 1
        storage.files_size += instance.size
        storage.save()


@receiver(post_delete, sender=File)
def file_delete(sender, instance, using, **kwargs):
    """
    Decrements storage file_count and file_size after File was deleted
    """
    try:
        if os.path.exists(instance.file_data.path):
            os.remove(instance.file_data.path)
    except ValueError as err:
        print(err)
    storage = instance.storage
    storage.files_count -= 1
    storage.files_size -= instance.size
    storage.save()
