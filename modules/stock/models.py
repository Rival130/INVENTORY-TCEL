from django.conf import settings
from django.db import models
from modules.products.models import Product
from modules.warehouse.models import Warehouse

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("product", "warehouse")

    def __str__(self):
        return f"{self.product} @ {self.warehouse}: {self.quantity}"


class StockMovement(models.Model):
    TYPE_CHOICES = [
        ("in", "Stock In"),
        ("out", "Stock Out"),
        ("adjust", "Adjustment"),
    ]
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)  # ex: invoice purchase
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]