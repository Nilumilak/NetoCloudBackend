import shutil

import pytest
from django.conf import settings

from files.models import File
from storage.models import Storage
from user.models import User


def teardown_function():
    """
    Delete created files during testing
    """
    try:
        shutil.rmtree("./media/test/")
    except FileNotFoundError:
        pass


@pytest.mark.django_db
def test_create_file_no_token(client, user_factory):
    """
    Create file without token
    """
    user_factory()
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
        }
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 401
        data = response.json()
        assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_create_file_regular_token(client, jwt_token_regular_factory):
    """
    Create file with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
            "path": "home/test/",
            "note": "test_note",
        }
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 201
        data = response.json()
        assert data.get("name") == "requirements.txt"
        assert data.get("note") == "test_note"
        assert data.get("path") == "home/test/"
        user = User.objects.get(username=user_data.get("username"))
        assert user.storage.files_count == 1
        assert user.storage.files_size == int(data.get("size"))
        response = client.delete(f"/api/v1/files/delete/{data.get('pk')}/")
        assert response.status_code == 204
        user = User.objects.get(username=user_data.get("username"))
        assert user.storage.files_count == 0
        assert user.storage.files_size == 0


@pytest.mark.django_db
def test_create_file_with_name_exists(client, jwt_token_regular_factory):
    """
    Create file with with existing name
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
        }
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 201
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
        }
        response = client.post("/api/v1/files/", data=data)
        data = response.json()
        assert response.status_code == 400
        assert data == {"error": "File with path '' and name 'requirements.txt' already exists."}


@pytest.mark.django_db
def test_create_file_with_name_and_path_exists(client, jwt_token_regular_factory):
    """
    Create file with with existing name in path
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {"file_data": file, "name": "requirements.txt", "path": "home/test/"}
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 201
    with open("./requirements.txt", "rb") as file:
        data = {"file_data": file, "name": "requirements.txt", "path": "home/test/"}
        response = client.post("/api/v1/files/", data=data)
        data = response.json()
        assert response.status_code == 400
        assert data == {"error": "File with path 'home/test/' and name 'requirements.txt' already exists."}


@pytest.mark.django_db
def test_get_uploaded_file(client, jwt_token_regular_factory):
    """
    Get uploaded file from storage without token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {"file_data": file, "name": "requirements.txt", "path": "home/test/"}
        response = client.post("/api/v1/files/", data=data)
        data = response.json()
        assert response.status_code == 201
        assert data.get("last_download") is None
    client.credentials(HTTP_AUTHORIZATION="")
    response = client.get(data.get("url_path"))
    assert response.status_code == 200
    assert File.objects.get(pk=data.get("pk")).last_download is not None


@pytest.mark.django_db
def test_update_uploaded_file_regular_token(client, jwt_token_regular_factory):
    """
    Update particular file with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
        }
        response = client.post("/api/v1/files/", data=data)
        data = response.json()
        assert response.status_code == 201
        assert data.get("note") == ""
        assert data.get("name") == "requirements.txt"
    update_data = {"name": "test_file.txt", "note": "test_note"}
    response = client.put(f'/api/v1/files/update/{data.get("pk")}/', data=update_data)
    data = response.json()
    assert response.status_code == 200
    assert data.get("name") == update_data.get("name")
    assert data.get("note") == update_data.get("note")


@pytest.mark.django_db
def test_update_uploaded_file_regular_token_other_file(client, user_factory, file_factory, jwt_token_regular_factory):
    """
    Update particular file of other owner with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    user = user_factory()
    file = file_factory(storage=user.storage)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    update_data = {"name": "test_file.txt", "note": "test_note"}
    response = client.put(f"/api/v1/files/update/{file.pk}/", data=update_data)
    data = response.json()
    assert response.status_code == 403
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_uploaded_file_admin_token_other_file(client, user_factory, file_factory, jwt_token_admin_factory):
    """
    Update particular of other owner file with admin token
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user = user_factory()
    file = file_factory(storage=user.storage, size=1000)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    update_data = {"name": "test_file.txt", "note": "test_note"}
    response = client.put(f"/api/v1/files/update/{file.pk}/", data=update_data)
    data = response.json()
    assert response.status_code == 200
    assert data.get("name") == update_data.get("name")
    assert data.get("note") == update_data.get("note")


@pytest.mark.django_db
def test_update_uploaded_file_with_same_name(client, user_factory, file_factory, jwt_token_admin_factory):
    """
    Update particular file with name that already exists in path
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user = user_factory()
    file1 = file_factory(storage=user.storage, size=1000, path="")
    file2 = file_factory(storage=user.storage, size=1000, path="")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    update_data = {
        "name": file1.name,
    }
    response = client.put(f"/api/v1/files/update/{file2.pk}/", data=update_data)
    data = response.json()
    assert response.status_code == 400
    assert data == {"error": f"File with path '' and name '{file1.name}' already exists."}


@pytest.mark.django_db
def test_delete_uploaded_file(client, user_factory, file_factory):
    """
    Delete uploaded file from storage without token
    """
    user = user_factory()
    file = file_factory(storage=user.storage)
    response = client.delete(f"/api/v1/files/delete/{file.pk}/")
    data = response.json()
    assert response.status_code == 401
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_delete_uploaded_file_regular_token(client, file_factory, jwt_token_regular_factory):
    """
    Delete particular file with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    storage = Storage.objects.get(id=user_data.get("storage_id"))
    file = file_factory(storage=storage)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.delete(f"/api/v1/files/delete/{file.pk}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_uploaded_file_regular_token_other_file(client, user_factory, file_factory, jwt_token_regular_factory):
    """
    Delete particular file of other owner with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    user = user_factory()
    file = file_factory(storage=user.storage)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.delete(f"/api/v1/files/delete/{file.pk}/")
    data = response.json()
    assert response.status_code == 403
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_delete_uploaded_file_admin_token_other_file(client, user_factory, file_factory, jwt_token_admin_factory):
    """
    Delete particular of other owner file with admin token
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user = user_factory()
    file = file_factory(storage=user.storage)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.delete(f"/api/v1/files/delete/{file.pk}/")
    assert response.status_code == 204


@pytest.mark.parametrize(
    ["path"],
    (("home/test./",), (r"home/te\st",), ("home",)),
)
@pytest.mark.django_db
def test_create_file_invalid_path_constraint(path, client, jwt_token_regular_factory):
    """
    Delete particular of other owner file with admin token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
            "path": path,
            "note": "test_note",
        }
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 400
        data = response.json()
        assert data == {"path": {"error": "Invalid path format. Forbidden symbols: '.', '\\'. Example: 'home/folder/path/'."}}


@pytest.mark.django_db
def test_max_storage_files_size_constraint(client, file_factory, jwt_token_regular_factory):
    """
    Delete particular of other owner file with admin token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    storage = Storage.objects.get(id=user_data.get("storage_id"))
    file = file_factory(storage=storage, size=settings.STORAGE_MAX_SIZE - 1, path="")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    with open("./requirements.txt", "rb") as file:
        data = {
            "file_data": file,
            "name": "requirements.txt",
            "path": "",
        }
        response = client.post("/api/v1/files/", data=data)
        assert response.status_code == 400
        data = response.json()
        assert data == {"error": f"User's storage is limited with max files_size value of {settings.STORAGE_MAX_SIZE // 1000000000} GB"}
