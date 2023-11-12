import pytest
from files.models import File


@pytest.mark.django_db
def test_create_file(user_factory, file_factory):
    """
    Create one File
    """
    user = user_factory()
    file = file_factory(storage=user.storage, size=100)

    assert File.objects.filter(id=file.pk).exists()
    assert user.storage.files_count == 1
    assert user.storage.files_size == file.size


@pytest.mark.django_db
def test_create_files(user_factory, file_factory):
    """
    Create many Files
    """
    user = user_factory()
    file = file_factory(_quantity=3, storage=user.storage, size=100)

    assert File.objects.count() == 3
    assert user.storage.files_count == 3
    assert user.storage.files_size == file[1].size * 3


@pytest.mark.django_db
def test_update_file(user_factory, file_factory):
    """
    Update File
    """
    user = user_factory()
    file = file_factory(storage=user.storage, size=100)

    file_db = File.objects.get(id=file.pk)
    file_db.name = 'update'
    file_db.note = 'update'
    file_db.save()

    updated_file = File.objects.get(id=file.pk)
    assert updated_file.name == 'update'
    assert updated_file.note == 'update'


@pytest.mark.django_db
def test_delete_file(user_factory, file_factory):
    """
    Delete File
    """
    user = user_factory()
    file = file_factory(storage=user.storage, size=100)
    File.objects.get(id=file.pk).delete()
    assert not File.objects.filter(id=file.pk).exists()
