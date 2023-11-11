import pytest
from model_bakery import baker
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
# address fixtures
from storage.models import Storage
from files.models import File
from user.models import User
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture
def user_factory():
    """
    User factory
    """
    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.fixture
def client():
    """
    Returns api client to perform requests
    """
    return APIClient()


@pytest.fixture()
def jwt_token_admin_facory(client):
    """
    JWT Admin Token Factory
    """
    def factory(username, email, full_name):
        data = {
            "username": username,
            "password": "testpassword!",
            "repeat_password": "testpassword!",
            "email": email,
            "full_name": full_name
        }
        response = client.post("/api/v1/users/", data=data, format="json")
        user = User.objects.first()
        user.is_staff = True
        user.save()
        response = client.post("/api/v1/token/", data=data, format="json")
        return {
            "token": response.json().get("access"),
            "id": user.pk,
            "username": user.username,
            "password": "testpassword!",
            "hash_password": user.password,
            "email": user.email,
            "full_name": user.full_name
        }
    return factory


@pytest.fixture()
def jwt_token_regular_factory(client):
    """
    JWT Regular User Token Factory
    """
    def factory(username, email, full_name):
        data = {
            "username": username,
            "password": "testpassword!",
            "repeat_password": "testpassword!",
            "email": email,
            "full_name": full_name
        }
        response = client.post("/api/v1/users/", data=data, format="json")
        user = User.objects.first()
        response = client.post("/api/v1/token/", data=data, format="json")
        return {
            "token": response.json().get("access"),
            "id": user.pk,
            "username": user.username,
            "password": "testpassword!",
            "hash_password": user.password,
            "email": user.email,
            "full_name": user.full_name
        }
    return factory