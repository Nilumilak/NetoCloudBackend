import pytest

from user.models import User


@pytest.mark.django_db
def test_create_user_api(client):
    """
    Create user with API post request
    """
    count = User.objects.count()
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": "test@test.ru",
        "full_name": "test_name",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 201
    assert User.objects.count() == count + 1
    reply = response.json()
    assert reply["username"] == data["username"]


@pytest.mark.django_db
def test_create_user_exists(client, user_factory):
    """
    Create already existing user
    """
    user = user_factory()
    data = {
        "username": user.username,
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": user.email,
        "full_name": "test_name",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply["username"] == ["user with this username already exists."]
    assert reply["email"] == ["A user with that email already exists."]


@pytest.mark.django_db
def test_create_user_less_info(client):
    """
    Create user with not all required information
    """
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": "test@test.ru",
        "full_name": "test_name",
    }
    data_copy = data.copy()
    for field in data:
        data_copy.pop(field)
        response = client.post("/api/v1/users/", data=data_copy, format="json")
        assert response.status_code == 400
        assert response.json() == {field: ["This field is required."]}
        data_copy = data.copy()


@pytest.mark.django_db
def test_create_user_null_info(client):
    """
    Create user with null required information
    """
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": "test@test.ru",
        "full_name": "test_name",
    }
    data_copy = data.copy()
    for field in ["username", "email", "full_name"]:
        data_copy[field] = None
        response = client.post("/api/v1/users/", data=data_copy, format="json")
        assert response.status_code == 400
        assert response.json() == {field: ["This field may not be null."]}
        data_copy = data.copy()


@pytest.mark.django_db
def test_create_user_blank_info(client):
    """
    Create user with blank required information
    """
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": "test@test.ru",
        "full_name": "test_name",
    }
    data_copy = data.copy()
    for field in ["username", "email", "full_name"]:
        data_copy[field] = ""
        response = client.post("/api/v1/users/", data=data_copy, format="json")
        assert response.status_code == 400
        assert response.json() == {field: ["This field may not be blank."]}
        data_copy = data.copy()


@pytest.mark.django_db
def test_create_user_email_validation(client):
    """
    Creation of user with invalid email
    """
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword!",
        "email": "email",
        "full_name": "test_name",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"email": ["Enter a valid email address."]}


@pytest.mark.parametrize(
    ["password", "expected_reply"],
    (
        (
            "93825647895217321596227862362245821005",
            {"password": ["This password is entirely numeric."]},
        ),
        (
            "strpa",
            {"password": ["This password is too short. It must contain at least 6 characters."]},
        ),
        ("password", {"password": ["This password is too common."]}),
    ),
)
@pytest.mark.django_db
def test_create_user_password_validation(client, password, expected_reply):
    """
    Creation of user with invalid password
    """
    data = {
        "username": "test",
        "password": password,
        "repeat_password": password,
        "email": "test@test.ru",
        "full_name": "test_name",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == expected_reply


@pytest.mark.django_db
def test_create_user_password_repeat_differs(client):
    """
    Creation of user with different repeat_password
    """
    data = {
        "username": "test",
        "password": "testpassword!",
        "repeat_password": "testpassword2!",
        "email": "email",
        "full_name": "test_name",
    }
    response = client.post("/api/v1/users/", data=data, format="json")
    assert response.status_code == 400
    reply = response.json()
    assert reply == {"password": ["Password fields does not match."]}


@pytest.mark.django_db
def test_list_users_no_token(client):
    """
    Get user list info without token
    """
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_list_users_wrong_token(client):
    """
    Get user list info with wrong token
    """
    client.credentials(HTTP_AUTHORIZATION="Bearer wrong_token")
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    data = response.json()
    assert data == {
        "code": "token_not_valid",
        "detail": "Given token not valid for any token type",
        "messages": [
            {
                "message": "Token is invalid or expired",
                "token_class": "AccessToken",
                "token_type": "access",
            }
        ],
    }


@pytest.mark.django_db
def test_list_users_admin(client, user_factory, jwt_token_admin_factory):
    """
    Get user list info with admin token
    """
    data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    users = user_factory(_quantity=5)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(users) + 1 == len(data)


@pytest.mark.django_db
def test_list_users_user(client, jwt_token_regular_factory):
    """
    Get user list info with user token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.get("/api/v1/users/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_retrieve_users_no_token(client, user_factory):
    """
    Get particular user info without token
    """
    user = user_factory()
    response = client.get(f"/api/v1/users/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_retrieve_users_wrong_token(client, user_factory):
    """
    Get particular user info with wrong token
    """
    user = user_factory()
    client.credentials(HTTP_AUTHORIZATION="Bearer wrong_token")
    response = client.get(f"/api/v1/users/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {
        "code": "token_not_valid",
        "detail": "Given token not valid for any token type",
        "messages": [
            {
                "message": "Token is invalid or expired",
                "token_class": "AccessToken",
                "token_type": "access",
            }
        ],
    }


@pytest.mark.django_db
def test_retrieve_users_user_token(client, jwt_token_regular_factory):
    """
    Get particular user info with user token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.get(f"/api/v1/users/{data.get('id')}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == data.get("id")


@pytest.mark.django_db
def test_retrieve_users_user_not_exist(client, jwt_token_admin_factory):
    """
    Get particular absent user info
    """
    data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.get("/api/v1/users/9999/")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_destroy_users_no_token(client, user_factory):
    """
    Delete particular user without token
    """
    user = user_factory()
    response = client.delete(f"/api/v1/users/delete/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_destroy_users_wrong_token(client, user_factory):
    """
    Delete particular user with wrong token
    """
    user = user_factory()
    client.credentials(HTTP_AUTHORIZATION="Bearer wrong_token/")
    response = client.delete(f"/api/v1/users/delete/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {
        "code": "token_not_valid",
        "detail": "Given token not valid for any token type",
        "messages": [
            {
                "message": "Token is invalid or expired",
                "token_class": "AccessToken",
                "token_type": "access",
            }
        ],
    }


@pytest.mark.django_db
def test_destroy_users_user_token(client, jwt_token_regular_factory):
    """
    Delete particular user with users token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.delete(f"/api/v1/users/delete/{data.get('id')}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_destroy_users_other_user_admin_token(client, user_factory, jwt_token_admin_factory):
    """
    Delete particular user with admin token
    """
    data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user2 = user_factory()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.delete(f"/api/v1/users/delete/{user2.id}/")
    assert response.status_code == 204
    delete_user = User.objects.get(id=user2.id)
    assert not delete_user.is_active


@pytest.mark.django_db
def test_destroy_users_other_user_token(client, user_factory, jwt_token_regular_factory):
    """
    Delete particular user with other users token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    user2 = user_factory()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.delete(f"/api/v1/users/delete/{user2.id}/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_destroy_users_user_not_exist(client, jwt_token_admin_factory):
    """
    Delete absent particular user
    """
    data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.delete("/api/v1/users/delete/9999/")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_users_no_token(client, user_factory):
    """
    Update particular user info without token
    """
    user = user_factory()
    response = client.patch(f"/api/v1/users/update/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_users_wrong_token(client, user_factory):
    """
    Update particular user info with wrong token
    """
    user = user_factory()
    client.credentials(HTTP_AUTHORIZATION="Bearer wrong_token/")
    response = client.patch(f"/api/v1/users/update/{user.id}/")
    assert response.status_code == 401
    data = response.json()
    assert data == {
        "code": "token_not_valid",
        "detail": "Given token not valid for any token type",
        "messages": [
            {
                "message": "Token is invalid or expired",
                "token_class": "AccessToken",
                "token_type": "access",
            }
        ],
    }


@pytest.mark.django_db
def test_update_users_other_user_token(client, user_factory, jwt_token_regular_factory):
    """
    Update particular user info with other users token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    user2 = user_factory()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.patch(f"/api/v1/users/update/{user2.id}/")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_users_user_token(client, jwt_token_regular_factory):
    """
    Update particular user info with users token
    """
    data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.patch(
        f"/api/v1/users/update/{data.get('id')}/",
        data={"username": "username"},
        format="json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "username"


@pytest.mark.django_db
def test_update_users_user_not_exist(client, jwt_token_admin_factory):
    """
    Update absent particular user info
    """
    data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {data.get('token')}")
    response = client.patch("/api/v1/users/update/999/", data={"username": "username"}, format="json")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Not found."}


@pytest.mark.django_db
def test_update_users_unique_fields(client, user_factory, jwt_token_admin_factory):
    """
    Update particular user unique fields to already existing values
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    user2 = user_factory()

    response = client.patch(
        f"/api/v1/users/update/{user_data.get('id')}/",
        data={"username": user2.username},
        format="json",
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"username": ["user with this username already exists."]}

    response = client.patch(
        f"/api/v1/users/update/{user_data.get('id')}/",
        data={"email": user2.email},
        format="json",
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"email": ["A user with that email already exists."]}


@pytest.mark.django_db
def test_update_users_email_validation(client, jwt_token_regular_factory):
    """
    Update particular user with invalid email
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    response = client.patch(
        f"/api/v1/users/update/{user_data.get('id')}/",
        data={"email": "email"},
        format="json",
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {"email": ["Enter a valid email address."]}


@pytest.mark.django_db
def test_update_users_null_fields(client, jwt_token_regular_factory):
    """
    Update particular user info with null fields
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    for field in ["username", "email"]:
        response = client.patch(
            f"/api/v1/users/update/{user_data.get('id')}/",
            data={field: None},
            format="json",
        )
        assert response.status_code == 400
        data = response.json()
        assert data == {field: ["This field may not be null."]}


@pytest.mark.django_db
def test_update_users_blank_fields(client, jwt_token_regular_factory):
    """
    Update particular user info with blank fields
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    for field in ["username", "email"]:
        response = client.patch(
            f"/api/v1/users/update/{user_data.get('id')}/",
            data={field: ""},
            format="json",
        )
        assert response.status_code == 400
        data = response.json()
        assert data == {field: ["This field may not be blank."]}


@pytest.mark.django_db
def test_update_users_password_patch(client, jwt_token_regular_factory):
    """
    Update particular user password
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    new_password = "VeryStrongPassword1!"
    patch_data = {
        "current_password": user_data.get("password"),
        "password": new_password,
        "repeat_password": new_password,
    }
    response = client.patch(f"/api/v1/users/update/{user_data.get('id')}/", data=patch_data, format="json")
    assert response.status_code == 200
    user = User.objects.get(id=user_data.get("id"))
    new_hash = user.password
    assert user_data.get("hash_password") != new_hash


@pytest.mark.django_db
def test_update_users_password_to_same_patch(client, jwt_token_regular_factory):
    """
    Update particular user password to same password
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    patch_data = {
        "current_password": user_data.get("password"),
        "password": user_data.get("password"),
        "repeat_password": user_data.get("password"),
    }
    response = client.patch(f"/api/v1/users/update/{user_data.get('id')}/", data=patch_data, format="json")
    assert response.status_code == 400
    data = response.json()
    assert data == {"password": ["New password cannot be the same as the old one"]}


@pytest.mark.django_db
def test_update_users_staff_status_change_no_token(client, user_factory):
    """
    Changing is_staff field without token
    """
    user = user_factory(is_staff=False)
    patch_data = {"is_staff": True}
    response = client.patch(f"/api/v1/users/update/{user.pk}/", data=patch_data, format="json")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication credentials were not provided."}


@pytest.mark.django_db
def test_update_users_staff_status_change_regular_token(client, jwt_token_regular_factory):
    """
    Changing is_staff field with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    patch_data = {"is_staff": True}
    response = client.patch(f"/api/v1/users/update/{user_data.get('id')}/", data=patch_data, format="json")
    assert response.status_code == 200
    data = response.json()
    assert "is_staff" not in data
    user = User.objects.get(username=user_data.get("username"))
    assert not user.is_staff


@pytest.mark.django_db
def test_update_other_users_staff_status_change_regular_token(client, user_factory, jwt_token_regular_factory):
    """
    Changing is_staff field of other user with regular token
    """
    user_data = jwt_token_regular_factory("test", "test@test.ru", "test_name")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    user = user_factory(is_staff=False)
    patch_data = {"is_staff": True}
    response = client.patch(f"/api/v1/users/update/{user.pk}/", data=patch_data, format="json")
    assert response.status_code == 403
    data = response.json()
    assert data == {"detail": "You do not have permission to perform this action."}


@pytest.mark.django_db
def test_update_other_users_staff_status_change_admin_token(client, user_factory, jwt_token_admin_factory):
    """
    Changing is_staff field of other user with admin token
    """
    user_data = jwt_token_admin_factory("test", "test@test.ru", "test_name")
    user = user_factory(is_staff=False)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_data.get('token')}")
    patch_data = {"is_staff": True}
    response = client.patch(f"/api/v1/users/update/{user.pk}/", data=patch_data, format="json")
    assert response.status_code == 200
    data = response.json()
    assert data.get("is_staff") is True
