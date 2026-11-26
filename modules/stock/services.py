# modules/stock/services.py  (file foun)
"""
Konvensaun kuantidade iha StockMovement:
  - "in"     : kuantidade pozitivu  -> stock sa'e
  - "out"    : kuantidade pozitivu  -> stock tun
  - "adjust" : kuantidade ho sinal  -> pozitivu = aumenta, negativu = hamenus

Hotu-hotu ne'ebé muda Stock.quantity tenke liu husi apply_movement()
atu iha istória (StockMovement) no stock la sai negativu.
"""
from django.db import transaction

from .models import Stock, StockMovement


class InsufficientStock(Exception):
    """Stock la sufisiente ba operasaun ne'e."""


def signed_delta(movement_type, quantity):
    if movement_type == "out":
        return -abs(quantity)
    if movement_type == "in":
        return abs(quantity)
    return quantity  # adjust: kuantidade ho sinal


@transaction.atomic
def apply_movement(*, product, warehouse, movement_type, quantity, user=None, reference="", note=""):
    stock, _ = Stock.objects.select_for_update().get_or_create(
        product=product, warehouse=warehouse
    )
    delta = signed_delta(movement_type, quantity)
    new_quantity = stock.quantity + delta
    if new_quantity < 0:
        raise InsufficientStock(
            f"Stock la sufisiente. Disponivel: {stock.quantity}, presiza: {abs(delta)}."
        )

    stock.quantity = new_quantity
    stock.save(update_fields=["quantity"])

    return StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference,
        note=note,
        created_by=user,
    )