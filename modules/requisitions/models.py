# modules/requisitions/models.py
"""
Rekizisaun = pedidu internu atu foti sasán husi armazén (ezemplu departamentu ida husu kuaderno 20).

Fluxu:  pending --aprova--> approved --entrega--> issued   (stock tun)
                  \--rejeita--> rejected
        pending/approved --kansela--> cancelled
"""
from django.conf import settings
from django.db import models
from django.utils import timezone

from modules.products.models import Product
from modules.warehouse.models import Warehouse


class Requisition(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("issued", "Issued"),
        ("cancelled", "Cancelled"),
    ]
    PRIORITY_CHOICES = [
        ("normal", "Normal"),
        ("urgent", "Urgent"),
    ]

    request_no = models.CharField(max_length=30, unique=True, editable=False)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="requisitions")
    department = models.CharField(max_length=100, blank=True)
    purpose = models.TextField(blank=True)
    needed_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="normal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="requisitions"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_requisitions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="issued_requisitions",
    )
    issued_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        permissions = [
            ("approve_requisition", "Can approve or reject requisitions"),
            ("issue_requisition", "Can issue (deliver) requisitions"),
        ]

    @classmethod
    def next_number(cls):
        year = timezone.localdate().year
        prefix = f"REQ-{year}-"
        last = (
            cls.objects.filter(request_no__startswith=prefix)
            .order_by("-request_no")
            .values_list("request_no", flat=True)
            .first()
        )
        seq = int(last.rsplit("-", 1)[1]) + 1 if last else 1
        return f"{prefix}{seq:04d}"

    def save(self, *args, **kwargs):
        if not self.request_no:
            self.request_no = self.next_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.request_no


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()                      # kuantidade husu
    approved_quantity = models.PositiveIntegerField(null=True, blank=True)  # kuantidade aprova (bele menus)

    @property
    def final_quantity(self):
        """Kuantidade ne'ebé sei entrega: aprova se iha, se la iha mak kuantidade husu."""
        return self.quantity if self.approved_quantity is None else self.approved_quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"