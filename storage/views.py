from rest_framework import generics
from .models import Storage
from .serializers import StorageListSerializer, StorageRetrieveSerializer
from .permissions import isStaffOrOwnerPermission
from user.permissions import isStaffEditorPermission


class StorageListView(generics.ListAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageListSerializer
    permission_classes = [isStaffEditorPermission]
    

class StorageRetrieveView(generics.RetrieveAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageRetrieveSerializer
    permission_classes = [isStaffOrOwnerPermission]
