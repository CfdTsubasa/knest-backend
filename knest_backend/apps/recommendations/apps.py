from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knest_backend.apps.recommendations'
    verbose_name = '推薦システム'
    
    def ready(self):
        # アプリケーション起動時の初期化処理
        pass 