from django.apps import AppConfig


class UserConfig(AppConfig):
    """
    Class representing user application and its configuration.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
