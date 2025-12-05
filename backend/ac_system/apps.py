from django.apps import AppConfig
import sys


class AcSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ac_system"

    def ready(self):
        if "runserver" in sys.argv:
            from .scheduler import scheduler

            scheduler.start()
