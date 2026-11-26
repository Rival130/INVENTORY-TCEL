# modules/requisitions/services.py  (file foun)
from django.db import transaction
from django.utils import timezone

from modules.stock.services import InsufficientStock, apply_movement

from .models import Requisition


class RequisitionError(Exception):
    """Operasaun ba rekizisaun la bele halo."""


# ---------- Permisaun ----------
def can_approve(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm("requisitions.approve_requisition"))


def can_issue(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm("requisitions.issue_requisition"))


def can_view(user, requisition):
    return (
        can_approve(user) or can_issue(user)
        or (requisition.requested_by_id is not None and requisition.requested_by_id == user.pk)
    )


# ---------- Operasaun ----------
@transaction.atomic
def approve_requisition(pk, user, approved=None, note=""):
    """
    approved = {item_id: kuantidade_aprova}. Se la iha, aprova kuantidade husu hotu.
    Kuantidade aprova bele menus (0 mós bele), maibé la bele liu kuantidade husu.
    """
    r = Requisition.objects.select_for_update().get(pk=pk)
    if r.status != "pending":
        raise RequisitionError("Rekizisaun ne'e la pendente ona.")

    items = list(r.items.select_related("product"))
    if not items:
        raise RequisitionError("Rekizisaun la iha item.")

    approved = approved or {}
    total = 0
    for item in items:
        qty = approved.get(item.pk, item.quantity)
        if qty < 0 or qty > item.quantity:
            raise RequisitionError(
                f"Kuantidade aprova ba “{item.product.name}” tenke entre 0 no {item.quantity}."
            )
        item.approved_quantity = qty
        total += qty
    if total == 0:
        raise RequisitionError("Kuantidade aprova hotu 0. Uza “Rejeita” se la aprova.")

    type(items[0]).objects.bulk_update(items, ["approved_quantity"])
    r.status = "approved"
    r.reviewed_by = user
    r.reviewed_at = timezone.now()
    r.review_note = note.strip()
    r.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    return r


@transaction.atomic
def reject_requisition(pk, user, note=""):
    r = Requisition.objects.select_for_update().get(pk=pk)
    if r.status != "pending":
        raise RequisitionError("Rekizisaun ne'e la pendente ona.")
    if not note.strip():
        raise RequisitionError("Prense razaun rejeita.")
    r.status = "rejected"
    r.reviewed_by = user
    r.reviewed_at = timezone.now()
    r.review_note = note.strip()
    r.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    return r


@transaction.atomic
def issue_requisition(pk, user):
    """Entrega sasán: halo movimentu "Sai" ba item hotu. Se ida falla, buat hotu rollback."""
    r = Requisition.objects.select_for_update().get(pk=pk)
    if r.status != "approved":
        raise RequisitionError("Rekizisaun tenke aprova molok entrega.")

    for item in r.items.select_related("product"):
        qty = item.final_quantity
        if qty <= 0:
            continue
        try:
            apply_movement(
                product=item.product,
                warehouse=r.warehouse,
                movement_type="out",
                quantity=qty,
                user=user,
                reference=r.request_no,
                note=f"Entrega rekizisaun {r.request_no}" + (f" · {r.department}" if r.department else ""),
            )
        except InsufficientStock as e:
            raise RequisitionError(f"{item.product.name}: {e}")

    r.status = "issued"
    r.issued_by = user
    r.issued_at = timezone.now()
    r.save(update_fields=["status", "issued_by", "issued_at", "updated_at"])
    return r


@transaction.atomic
def cancel_requisition(pk, user):
    r = Requisition.objects.select_for_update().get(pk=pk)
    is_owner = r.requested_by_id == user.pk
    if r.status == "pending":
        if not (is_owner or can_approve(user)):
            raise RequisitionError("Ita-boot la iha permisaun atu kansela rekizisaun ne'e.")
    elif r.status == "approved":
        if not can_approve(user):
            raise RequisitionError("Aprovadór de'it mak bele kansela rekizisaun ne'ebé aprova ona.")
    else:
        raise RequisitionError("Rekizisaun ne'e la bele kansela ona.")
    r.status = "cancelled"
    r.save(update_fields=["status", "updated_at"])
    return r