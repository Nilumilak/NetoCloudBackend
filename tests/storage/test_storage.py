import pytest


@pytest.mark.django_db
def test_storage_list_view_no_token(client):
    """
    Get storage list without token
    """
    response = client.get("/api/v1/storages/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_storage_list_view_admin(client, jwt_token_admin_factory):
    """
    Get storage list with admin token
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.get("/api/v1/storages/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.django_db
def test_storage_list_view_regular(client, jwt_token_regular_factory):
    """
    Get storage list with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.get("/api/v1/storages/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_storage_retrieve_view_not_exists(client):
    """
    Get storage that does not exist
    """
    response = client.get("/api/v1/storages/1/")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_storage_retrieve_view_no_token(client, user_factory):
    """
    Get particular storage without token
    """
    user = user_factory()
    response = client.get(f"/api/v1/storages/{user.storage.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_storage_retrieve_view_regular(client, jwt_token_regular_factory):
    """
    Get particular storage with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    storage_id = client.get(f"/api/v1/users/{user_data.get('username')}/").json().get("storage_id")
    response = client.get(f"/api/v1/storages/{storage_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("files_count") == 0
    assert data.get("files_size") == 0
    assert data.get("owner").get("username") == user_data.get("username")


@pytest.mark.django_db
def test_storage_other_user_retrieve_view_regular(client, user_factory, jwt_token_regular_factory):
    """
    Get particular storage of other user with regular token
    """
    user_data1 = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    user_data2 = user_factory()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data1.get('token')}")
    response = client.get(f"/api/v1/storages/{user_data2.storage.pk}/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_storage_other_user_retrieve_view_admin(client, user_factory, jwt_token_admin_factory):
    """
    Get particular storage of other user with admin token
    """
    user_data1 = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user_data2 = user_factory()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data1.get('token')}")
    response = client.get(f"/api/v1/storages/{user_data2.storage.pk}/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("files_count") == 0
    assert data.get("files_size") == 0
    assert data.get("owner").get("username") == user_data2.username
