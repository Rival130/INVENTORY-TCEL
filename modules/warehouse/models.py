from django.conf import settings
from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="managed_warehouses",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name