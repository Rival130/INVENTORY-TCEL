from django.contrib import admin
from .models import Warehouse

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "manager", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "location")