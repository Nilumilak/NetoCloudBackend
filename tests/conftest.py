import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from files.models import File
from user.models import User


@pytest.fixture
def user_factory():
    """
    User factory
    """

    def factory(*args, **kwargs):
        return baker.make(User, *args, **kwargs)

    return factory


@pytest.fixture
def file_factory():
    """
    User factory
    """

    def factory(*args, **kwargs):
        return baker.make(File, *args, **kwargs)

    return factory


@pytest.fixture
def client():
    """
    Returns api client to perform requests
    """
    return APIClient()


@pytest.fixture()
def jwt_token_admin_factory():
    """
    JWT Admin Token Factory
    """

    def factory(username, email, full_name):
        api_client = APIClient()
        data = {
            "username": username,
            "password": "testpassword!",
            "repeat_password": "testpassword!",
            "email": email,
            "full_name": full_name,
        }
        response = api_client.post("/api/v1/users/", data=data, format="json")
        user = User.objects.first()
        assert user is not None
        user.is_staff = True
        user.save()
        response = api_client.post("/api/v1/token/", data=data, format="json")
        return {
            "token": response.json().get("access"),
            "id": user.pk,
            "username": user.username,
            "password": "testpassword!",
            "hash_password": user.password,
            "email": user.email,
            "full_name": user.full_name,
            "storage_id": user.storage.pk,
        }

    return factory


@pytest.fixture()
def jwt_token_regular_factory():
    """
    JWT Regular User Token Factory
    """

    def factory(username, email, full_name):
        api_client = APIClient()
        data = {
            "username": username,
            "password": "testpassword!",
            "repeat_password": "testpassword!",
            "email": email,
            "full_name": full_name,
        }
        response = api_client.post("/api/v1/users/", data=data, format="json")
        user = User.objects.first()
        assert user is not None
        response = api_client.post("/api/v1/token/", data=data, format="json")
        return {
            "token": response.json().get("access"),
            "id": user.pk,
            "username": user.username,
            "password": "testpassword!",
            "hash_password": user.password,
            "email": user.email,
            "full_name": user.full_name,
            "storage_id": user.storage.pk,
        }

    return factory
