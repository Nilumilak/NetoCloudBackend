from rest_framework import serializers
from .models import Storage
from files.serializers import FileSerializer
from user.serializers import UserSerializer


class StorageListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = Storage
        fields = ['pk', 'files_count', 'files_size', 'owner']
        

class StorageRetrieveSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    files = FileSerializer(many=True)
    
    class Meta:
        model = Storage
        fields = ['pk', 'files_count', 'files_size', 'owner', 'files']
