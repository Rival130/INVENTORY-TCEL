# modules/reports/services.py  (file foun)
from django.db import transaction
from django.utils import timezone

from modules.products.models import Product
from modules.stock.models import Stock

from .models import PriceHistory, StockSnapshot


@transaction.atomic
def take_snapshot(snapshot_date=None):
    """
    Foto stock hotu iha data ne'e (default: ohin). Bele halo dala barak iha loron ida:
    sei atualiza snapshot data ne'e nian (idempotent).
    Retorna (data, númeru liña).
    """
    day = snapshot_date or timezone.localdate()
    count = 0
    for stock in Stock.objects.select_related("product"):
        StockSnapshot.objects.update_or_create(
            date=day,
            product=stock.product,
            warehouse=stock.warehouse,
            defaults={"quantity": stock.quantity, "unit_cost": stock.product.purchase_price},
        )
        count += 1
    return day, count


@transaction.atomic
def init_price_history():
    """Kria istória folin inisiál ba produtu ne'ebé seidauk iha rekordu (uza ba dala ida de'it)."""
    created = 0
    existing = set(PriceHistory.objects.values_list("product_id", flat=True))
    for p in Product.objects.exclude(pk__in=existing):
        PriceHistory.objects.create(
            product=p, purchase_price=p.purchase_price, selling_price=p.selling_price
        )
        created += 1
    return created