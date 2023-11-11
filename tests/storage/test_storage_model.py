import pytest
from django.db import IntegrityError
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
def test_storage_increment_files_count(user_factory, file_factory):
    """
    Storage files_count increments when a file added to Storage
    """
    user = user_factory()
    file_factory(storage=user.storage, size=1000)
    assert user.storage.files_count == 1
    file_factory(storage=user.storage, size=2000)
    assert user.storage.files_count == 2


@pytest.mark.django_db
def test_storage_increment_files_size(user_factory, file_factory):
    """
    Storage files_size increments when a file added to Storage
    """
    user = user_factory()
    file1 = file_factory(storage=user.storage, size=1000)
    assert user.storage.files_size == file1.size
    file2 = file_factory(storage=user.storage, size=2000)
    assert user.storage.files_size == file1.size + file2.size


@pytest.mark.django_db
def test_storage_deletes_with_user(user_factory, file_factory):
    """
    User's storage deletes with User
    """
    user_factory()
    assert Storage.objects.all().exists()
    User.objects.first().delete()
    assert not Storage.objects.all().exists()
