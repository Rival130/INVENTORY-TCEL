from django.contrib import admin
from .models import Stock, StockMovement

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "low_stock")
    list_filter = ("warehouse",)
    search_fields = ("product__name", "product__sku")

    @admin.display(boolean=True, description="Stock ki'ik?")
    def low_stock(self, obj):
        return obj.quantity <= obj.product.min_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "movement_type", "quantity", "reference", "created_by", "created_at")
    list_filter = ("movement_type", "warehouse", "created_at")
    search_fields = ("product__name", "product__sku", "reference")
    readonly_fields = ("created_by", "created_at")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)