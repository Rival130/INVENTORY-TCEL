from django.conf import settings
from django.db import models
from modules.suppliers.models import Supplier
from modules.warehouse.models import Warehouse
from modules.products.models import Product

class Purchase(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]
    invoice_no = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchases")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="purchases")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="purchases"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return self.invoice_no


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product} x {self.quantity}"