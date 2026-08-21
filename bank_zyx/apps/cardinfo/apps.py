from django.apps import AppConfig

class CardInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cardinfo'  # ✅ 必须和 INSTALLED_APPS 一致