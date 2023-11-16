from rest_framework import serializers

from files.serializers import FileSerializer
from user.serializers import UserSerializer
from django.conf import settings

from .models import Storage


class StorageListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    max_size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Storage
        fields = ["pk", "files_count", "files_size", "max_size", "owner"]
    
    def get_max_size(self, obj):
        """
        Returns data for max_size field
        """
        return settings.STORAGE_MAX_SIZE


class StorageRetrieveSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    files = FileSerializer(many=True)
    max_size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Storage
        fields = ["pk", "files_count", "files_size", "max_size", "owner", "files"]
    
    def get_max_size(self, obj):
        """
        Returns data for max_size field
        """
        return settings.STORAGE_MAX_SIZE
