from django.apps import AppConfig


class AISupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knest_backend.apps.ai_support'
    verbose_name = 'AIサポート'

    def ready(self):
        """
        アプリケーションの初期化時に実行される処理
        """
        try:
            # シグナルの登録
            from . import signals
        except ImportError:
            pass 