import pytest
from django.db import IntegrityError

from files.models import File
from storage.models import Storage
from user.models import User


@pytest.mark.django_db
def test_create_storage(user_factory):
    """
    Storage is created with user
    """
    user = user_factory()
    assert Storage.objects.filter(id=user.storage.id).exists()
    assert Storage.objects.get(id=user.storage.id).files_count == 0
    assert Storage.objects.get(id=user.storage.id).files_size == 0


@pytest.mark.django_db
def test_storage_one_to_one_constraint(user_factory):
    """
    User can only have one storage
    """
    user = user_factory()
    try:
        Storage.objects.create(owner=user)
        assert False
    except IntegrityError:
        assert True


@pytest.mark.django_db
def test_storage_deletes_with_user(user_factory, file_factory):
    """
    User's storage deletes with User
    """
    user_factory()
    assert Storage.objects.all().exists()
    User.objects.first().delete()
    assert not Storage.objects.all().exists()
