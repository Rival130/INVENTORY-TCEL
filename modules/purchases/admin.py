from django.contrib import admin
from .models import Purchase, PurchaseItem

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    autocomplete_fields = ("product",)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "supplier", "warehouse", "date", "status", "total", "created_by")
    list_filter = ("status", "supplier", "warehouse", "date")
    search_fields = ("invoice_no", "supplier__name")
    date_hierarchy = "date"
    inlines = [PurchaseItemInline]
    readonly_fields = ("created_by", "created_at")

    def save_model(self, request, obj, form, change):
        if not change:  # kuandu kria foun de'it
            obj.created_by = request.user
        super().save_model(request, obj, form, change)