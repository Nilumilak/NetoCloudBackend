import pytest
from django.db import IntegrityError

from user.models import User


@pytest.mark.django_db
def test_create_user(user_factory):
    """
    Create one User
    """
    user = user_factory()

    assert User.objects.filter(id=user.pk).exists()


@pytest.mark.django_db
def test_create_users(user_factory):
    """
    Create many Users
    """
    user_factory(_quantity=3)

    assert User.objects.count() == 3


@pytest.mark.django_db
def test_update_user(user_factory):
    """
    Update User
    """
    user = user_factory()

    user_db = User.objects.get(id=user.pk)
    user_db.username = "update"
    user_db.email = "update@update.com"
    user_db.full_name = "update"
    user_db.save()

    updated_user = User.objects.get(id=user.pk)
    assert updated_user.username == "update"
    assert updated_user.email == "update@update.com"
    assert updated_user.full_name == "update"


@pytest.mark.django_db
def test_delete_user(user_factory):
    """
    Delete User
    """
    user = user_factory()
    User.objects.get(id=user.pk).delete()

    assert not User.objects.filter(id=user.pk).exists()


@pytest.mark.django_db
def test_user_username_unique_constraint(user_factory):
    """
    User username should be unique
    """
    user = user_factory()

    try:
        user_factory(username=user.username)
        assert False
    except IntegrityError:
        assert True


@pytest.mark.django_db
def test_user_email_unique_constraint(user_factory):
    """
    User email should be unique
    """
    user = user_factory()

    try:
        user_factory(email=user.email)
        assert False
    except IntegrityError:
        assert True
