from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "name", "category", "unit",
        "purchase_price", "selling_price", "min_stock", "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name")
    list_editable = ("purchase_price", "selling_price", "is_active")
    readonly_fields = ("created_at", "updated_at")