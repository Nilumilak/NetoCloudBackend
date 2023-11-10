from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


class User(AbstractUser):
    """
    Class to describe user
    """
    username = models.CharField(max_length=20, unique=True, validators=[MinLengthValidator(4)])
    full_name = models.CharField(max_length=50)
    email = models.EmailField(
        unique=True,
        error_messages={"unique": "A user with that email already exists.", }
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "full_name"]

    def __str__(self):
        return f"{self.username} {self.email}"
