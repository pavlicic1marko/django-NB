import atexit
import logging

from django.apps import AppConfig

logger = logging.getLogger('webapp')


class WebappConfig(AppConfig):
    name = 'webapp'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        logger.info("Application starting")
        atexit.register(lambda: logger.info("Application stopping"))
