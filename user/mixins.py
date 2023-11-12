from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response


class PasswordValidatorMixin:
    def password_validator(self, request):
        """
        Validates entered passwords
        """
        raw_password1 = request.data.get("password")
        raw_password2 = request.data.get("repeat_password")
        if not raw_password1:
            return Response(
                {"password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not raw_password2:
            return Response(
                {"repeat_password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if raw_password1 != raw_password2:
            return Response(
                {"password": ["Passwort fields does not match."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data.get("current_password") == raw_password1:
            return Response(
                {"password": ["New passport cannot be the same as the old one"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            validate_password(raw_password1)
            return None
        except ValidationError as errors:
            return Response({"password": list(errors)}, status=status.HTTP_400_BAD_REQUEST)
