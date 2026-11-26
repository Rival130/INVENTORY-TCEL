# modules/reports/apps.py
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.reports"
    verbose_name = "Reports"

    def ready(self):
        from . import signals  # noqa: F401  (rejistu signal istória folin)


# Iha settings.py INSTALLED_APPS:
#   "modules.reports",
# Depois: python manage.py makemigrations reports && python manage.py migrate