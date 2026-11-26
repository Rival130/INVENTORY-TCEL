# modules/purchases/services.py  (file foun)
from django.db import transaction

from modules.stock.services import apply_movement

from .models import Purchase


class PurchaseError(Exception):
    """Operasaun ba sosa la bele halo."""


@transaction.atomic
def receive_purchase(purchase_id, user=None):
    """
    Marka sosa hanesan "received" no tau stock tama (movimentu "in")
    ba produtu hotu iha armazén sosa nian. Hotu-hotu iha transasaun ida:
    se ida falla, buat hotu rollback.
    """
    purchase = Purchase.objects.select_for_update().get(pk=purchase_id)
    if purchase.status != "pending":
        raise PurchaseError("Sosa ne'e la pendente ona, la bele simu.")

    items = list(purchase.items.select_related("product"))
    if not items:
        raise PurchaseError("Sosa ne'e la iha item.")

    for item in items:
        apply_movement(
            product=item.product,
            warehouse=purchase.warehouse,
            movement_type="in",
            quantity=item.quantity,
            user=user,
            reference=purchase.invoice_no,
            note=f"Simu husi sosa {purchase.invoice_no}",
        )

    purchase.status = "received"
    purchase.save(update_fields=["status"])
    return purchase


@transaction.atomic
def cancel_purchase(purchase_id):
    """Sosa pendente de'it mak bele kansela (stock seidauk muda)."""
    purchase = Purchase.objects.select_for_update().get(pk=purchase_id)
    if purchase.status != "pending":
        raise PurchaseError("Sosa pendente de'it mak bele kansela.")
    purchase.status = "cancelled"
    purchase.save(update_fields=["status"])
    return purchase