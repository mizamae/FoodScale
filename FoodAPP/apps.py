from django.apps import AppConfig
import logging
logger = logging.getLogger("models")


class FoodAPPConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FoodAPP'

    def ready(self):
        import FoodAPP.signal_handlers
        #from .tasks import loadDefaultObjects
        #loadDefaultObjects()

