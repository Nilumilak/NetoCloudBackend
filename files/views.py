import os

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import File
from .permissions import IsStaffOrOwnerPermission
from .serializers import FileSerializer, FileUpdateSerializer


class FileCreateView(generics.CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]


class FileDownloadView(generics.RetrieveAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = "url"

    def get(self, request, *args, **kwargs):
        file_obj = self.get_object()
        file_path = os.path.join(settings.MEDIA_ROOT, *file_obj.file_data.name.split("/"))
        if os.path.exists(file_path):
            file_obj.last_download = timezone.now()
            file_obj.save()
            with open(file_path, "rb") as fh:
                response = HttpResponse(fh.read(), content_type=file_obj.content_type)
                response["Content-Disposition"] = "inline; filename=" + file_obj.name
                return response
        else:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class FileUpdateView(generics.UpdateAPIView):
    queryset = File.objects.all()
    serializer_class = FileUpdateSerializer
    permission_classes = [IsStaffOrOwnerPermission]


class FileDestroyView(generics.DestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsStaffOrOwnerPermission]
