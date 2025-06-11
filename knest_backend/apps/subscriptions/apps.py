from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knest_backend.apps.subscriptions'
    verbose_name = 'サブスクリプション'

    def ready(self):
        try:
            from . import signals  # noqa
        except ImportError:
            pass 