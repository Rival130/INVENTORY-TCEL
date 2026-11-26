# modules/reports/models.py
"""
Modelu ba akumula istória importante atu uza iha relatóriu.

Tansá presiza?
  - Stock.quantity rai de'it kuantidade ATUÁL. Se ita hakarak hatene stock iha fim fulan,
    ka valór stock tuir folin sosa iha tempu ne'ebá, presiza rai "foto" (snapshot) regulár.
  - Product.purchase_price / selling_price muda ba tempu. Se la rai istória, relatóriu
    folin, margen no valór stock iha pasadu sai la loos.

Istória seluk iha ona: StockMovement (movimentu stock), Purchase/PurchaseItem (sosa).
"""
from django.conf import settings
from django.db import models

from modules.products.models import Product
from modules.warehouse.models import Warehouse


class StockSnapshot(models.Model):
    """Foto stock loron-loron (ka fulan-fulan): kuantidade no folin sosa iha data ne'e."""

    date = models.DateField(db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="snapshots")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="snapshots")
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # purchase_price iha data ne'e
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "product__name"]
        unique_together = ("date", "product", "warehouse")
        indexes = [models.Index(fields=["product", "warehouse", "date"])]

    @property
    def value(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        return f"{self.date} · {self.product} @ {self.warehouse}: {self.quantity}"


class PriceHistory(models.Model):
    """Istória folin produtu: rekorda bainhira produtu kria ka folin sosa/faan muda."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_history")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="price_changes",
    )

    class Meta:
        ordering = ["-changed_at", "-id"]
        verbose_name_plural = "price history"

    @property
    def margin_percent(self):
        if self.purchase_price and self.purchase_price > 0:
            return (self.selling_price - self.purchase_price) / self.purchase_price * 100
        return None

    def __str__(self):
        return f"{self.product} · {self.changed_at:%Y-%m-%d}"