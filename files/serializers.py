import re

from django.conf import settings
from rest_framework import serializers

from .models import File


class FileSerializer(serializers.ModelSerializer):
    file_data = serializers.FileField(write_only=True)
    content_type = serializers.CharField(read_only=True)
    size = serializers.CharField(read_only=True)
    owner = serializers.SerializerMethodField(read_only=True)
    origin_name = serializers.CharField(read_only=True)

    class Meta:
        model = File
        fields = [
            "pk",
            "name",
            "origin_name",
            "content_type",
            "size",
            "path",
            "url_path",
            "note",
            "last_download",
            "created_at",
            "owner",
            "file_data",
        ]

    def validate_path(self, attrs):
        """
        Path validation
        """
        path_pattern = re.compile(r"(?:^[^\.\\]+/)+$")
        if not path_pattern.match(attrs) and attrs != "":
            raise serializers.ValidationError({"error": "Invalid path format. Forbidden symbols: '.', '\\'. Example: 'home/folder/path/'."})
        return attrs

    def create(self, validated_data):
        obj = File.objects.filter(path=validated_data.get("path", ""), name=validated_data.get("name"))
        if obj.exists():
            raise serializers.ValidationError(
                {"error": f"File with path '{validated_data.get('path', '')}' and name '{validated_data.get('name')}' already exists."}
            )

        validated_data["origin_name"] = self.context.get("request").FILES.get("file_data").name
        validated_data["size"] = self.context.get("request").FILES.get("file_data").size
        validated_data["content_type"] = self.context.get("request").FILES.get("file_data").content_type
        validated_data["storage"] = self.context.get("request").user.storage
        if validated_data["storage"].files_size + validated_data["size"] > settings.STORAGE_MAX_SIZE:
            raise serializers.ValidationError(
                {"error": f"User's storage is limited with max files_size value of {settings.STORAGE_MAX_SIZE // 1000000000} GB"}
            )
        return super().create(validated_data)

    def get_owner(self, obj):
        """
        Returns data for owner field
        """
        return {
            "username": obj.storage.owner.username,
            "email": obj.storage.owner.email,
        }


class FileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["pk", "name", "note"]

    def update(self, instance, validated_data):
        name = validated_data.get("name")
        if name:
            obj = File.objects.filter(path=instance.path, name=name)
            if obj.exists():
                raise serializers.ValidationError({"error": f"File with path '{instance.path}' and name '{name}' already exists."})
        return super().update(instance, validated_data)
