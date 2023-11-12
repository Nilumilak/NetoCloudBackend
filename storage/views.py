from rest_framework import generics

from user.permissions import isStaffEditorPermission

from .models import Storage
from .permissions import IsStaffOrOwnerPermission
from .serializers import StorageListSerializer, StorageRetrieveSerializer


class StorageListView(generics.ListAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageListSerializer
    permission_classes = [isStaffEditorPermission]


class StorageRetrieveView(generics.RetrieveAPIView):
    queryset = Storage.objects.all()
    serializer_class = StorageRetrieveSerializer
    permission_classes = [IsStaffOrOwnerPermission]
