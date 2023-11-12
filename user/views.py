from django.contrib.auth.hashers import check_password, make_password
from rest_framework import generics, status
from rest_framework.response import Response

from user.permissions import isStaffEditorPermission, isStaffOrUserPermission

from .mixins import PasswordValidatorMixin
from .models import User
from .serializers import UserSerializer, UserSerializerAdmin


class UserListCreateView(generics.ListAPIView, generics.CreateAPIView, PasswordValidatorMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [isStaffEditorPermission]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return UserSerializerAdmin
        return UserSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return []
        return super().get_permissions()

    def perform_create(self, serializer, **kwargs):
        serializer.save(**kwargs)

    def create(self, request, *args, **kwargs):
        response = self.password_validator(request)
        if response:
            return response
        password = make_password(request.data.get("password"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, password=password)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailedView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [isStaffOrUserPermission]
    lookup_field = "username"


class UserUpdateView(generics.UpdateAPIView, PasswordValidatorMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [isStaffOrUserPermission]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if request.data.get("password"):
            current_password = request.data.get("current_password")
            if not check_password(current_password, request.user.password):
                return Response(
                    {"password": ["Invalid password."]},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            response = self.password_validator(request)
            if response:
                return response
            password = make_password(request.data.get("password"))
            self.perform_update(serializer, password=password)
        else:
            self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer, **kwargs):
        serializer.save(**kwargs)


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [isStaffOrUserPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
