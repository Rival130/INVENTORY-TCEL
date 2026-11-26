# modules/reports/signals.py  (file foun)
"""
Rekorda istória folin automátiku bainhira Product kria ka folin muda.

Opsionál: atu rekorda utilizadór ne'ebé muda, iha view produtu tau
    product._changed_by = request.user
molok product.save().
"""
from decimal import Decimal

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from modules.products.models import Product

from .models import PriceHistory


def _dec(value):
    return Decimal(str(value)) if value is not None else Decimal("0")


@receiver(pre_save, sender=Product)
def remember_old_prices(sender, instance, **kwargs):
    old = None
    if instance.pk:
        row = (
            Product.objects.filter(pk=instance.pk)
            .values("purchase_price", "selling_price")
            .first()
        )
        if row:
            old = (_dec(row["purchase_price"]), _dec(row["selling_price"]))
    instance._old_prices = old


@receiver(post_save, sender=Product)
def record_price_history(sender, instance, created, **kwargs):
    new = (_dec(instance.purchase_price), _dec(instance.selling_price))
    old = getattr(instance, "_old_prices", None)
    if created or old != new:
        PriceHistory.objects.create(
            product=instance,
            purchase_price=new[0],
            selling_price=new[1],
            changed_by=getattr(instance, "_changed_by", None),
        )