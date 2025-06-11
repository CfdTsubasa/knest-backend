from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knest_backend.apps.users'
    verbose_name = 'ユーザー管理' 