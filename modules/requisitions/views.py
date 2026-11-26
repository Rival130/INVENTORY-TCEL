# modules/requisitions/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from modules.stock.models import Stock

from .forms import RequisitionForm, RequisitionItemEditFormSet, RequisitionItemFormSet
from .models import Requisition
from .services import (
    RequisitionError, approve_requisition, can_approve, can_issue, can_view,
    cancel_requisition, issue_requisition, reject_requisition,
)


def _get_visible(request, pk):
    r = get_object_or_404(
        Requisition.objects.select_related("warehouse", "requested_by", "reviewed_by", "issued_by"), pk=pk
    )
    if not can_view(request.user, r):
        raise Http404
    return r


@login_required
def requisition_list(request):
    qs = Requisition.objects.select_related("warehouse", "requested_by").prefetch_related("items")
    # Pengguna ordinária haree de'it nia rekizisaun rasik; aprovadór/entregadór haree hotu
    if not (can_approve(request.user) or can_issue(request.user)):
        qs = qs.filter(requested_by=request.user)

    requisitions = list(qs)
    approver = can_approve(request.user)
    for r in requisitions:
        r.item_count = len(r.items.all())  # prefetch: la iha query tan
        r.can_edit = r.status == "pending" and (approver or r.requested_by_id == request.user.pk)

    return render(request, "requisitions/requisition_list.html", {
        "requisitions": requisitions,
        "can_approve": can_approve(request.user),
        "see_all": can_approve(request.user) or can_issue(request.user),
    })


@login_required
def requisition_detail(request, pk):
    r = _get_visible(request, pk)
    items = list(r.items.select_related("product"))

    # Stock disponivel iha armazén ba kada item
    stock_map = dict(
        Stock.objects.filter(warehouse=r.warehouse, product__in=[i.product_id for i in items])
        .values_list("product_id", "quantity")
    )
    shortage = False
    for i in items:
        i.available = stock_map.get(i.product_id, 0)
        i.short = r.status in ("pending", "approved") and i.final_quantity > i.available
        shortage = shortage or (r.status == "approved" and i.final_quantity > i.available)

    is_owner = r.requested_by_id == request.user.pk
    return render(request, "requisitions/requisition_detail.html", {
        "r": r,
        "items": items,
        "total_requested": sum(i.quantity for i in items),
        "total_final": sum(i.final_quantity for i in items),
        "shortage": shortage,
        "is_owner": is_owner,
        "can_approve": can_approve(request.user),
        "can_issue": can_issue(request.user),
        "can_edit": r.status == "pending" and (is_owner or can_approve(request.user)),
        "can_cancel": (r.status == "pending" and (is_owner or can_approve(request.user)))
                      or (r.status == "approved" and can_approve(request.user)),
    })


@login_required
def requisition_create(request):
    requisition = Requisition()
    form = RequisitionForm(request.POST or None)
    formset = RequisitionItemFormSet(request.POST or None, instance=requisition)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            requisition = form.save(commit=False)
            requisition.requested_by = request.user
            requisition.save()
            formset.instance = requisition
            formset.save()
        messages.success(request, f"Rekizisaun “{requisition.request_no}” haruka ona. Hein aprovasaun.")
        return redirect("requisitions:requisition_detail", pk=requisition.pk)

    return render(request, "requisitions/requisition_form.html", {
        "form": form, "formset": formset, "title": "Rekizisaun Foun",
    })


@login_required
def requisition_update(request, pk):
    requisition = _get_visible(request, pk)
    is_owner = requisition.requested_by_id == request.user.pk
    if requisition.status != "pending" or not (is_owner or can_approve(request.user)):
        messages.error(request, "Rekizisaun ne'e la bele edita ona.")
        return redirect("requisitions:requisition_detail", pk=pk)

    form = RequisitionForm(request.POST or None, instance=requisition)
    formset = RequisitionItemEditFormSet(request.POST or None, instance=requisition)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
        messages.success(request, f"Rekizisaun “{requisition.request_no}” atualiza ona.")
        return redirect("requisitions:requisition_detail", pk=pk)

    return render(request, "requisitions/requisition_form.html", {
        "form": form, "formset": formset, "title": f"Edita {requisition.request_no}",
    })


# ---------- Aksaun (POST de'it) ----------
@login_required
@require_POST
def requisition_approve(request, pk):
    _get_visible(request, pk)
    if not can_approve(request.user):
        messages.error(request, "Ita-boot la iha permisaun atu aprova.")
        return redirect("requisitions:requisition_detail", pk=pk)

    approved = {}
    for key, value in request.POST.items():
        if key.startswith("approved_"):
            try:
                approved[int(key.split("_", 1)[1])] = int(value)
            except ValueError:
                messages.error(request, "Kuantidade aprova tenke númeru.")
                return redirect("requisitions:requisition_detail", pk=pk)
    try:
        r = approve_requisition(pk, request.user, approved=approved, note=request.POST.get("note", ""))
    except RequisitionError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Rekizisaun “{r.request_no}” aprova ona.")
    return redirect("requisitions:requisition_detail", pk=pk)


@login_required
@require_POST
def requisition_reject(request, pk):
    _get_visible(request, pk)
    if not can_approve(request.user):
        messages.error(request, "Ita-boot la iha permisaun atu rejeita.")
        return redirect("requisitions:requisition_detail", pk=pk)
    try:
        r = reject_requisition(pk, request.user, note=request.POST.get("note", ""))
    except RequisitionError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Rekizisaun “{r.request_no}” rejeita ona.")
    return redirect("requisitions:requisition_detail", pk=pk)


@login_required
@require_POST
def requisition_issue(request, pk):
    _get_visible(request, pk)
    if not can_issue(request.user):
        messages.error(request, "Ita-boot la iha permisaun atu entrega sasán.")
        return redirect("requisitions:requisition_detail", pk=pk)
    try:
        r = issue_requisition(pk, request.user)
    except RequisitionError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Rekizisaun “{r.request_no}” entrega ona. Stock atualiza ona.")
    return redirect("requisitions:requisition_detail", pk=pk)


@login_required
@require_POST
def requisition_cancel(request, pk):
    _get_visible(request, pk)
    try:
        r = cancel_requisition(pk, request.user)
    except RequisitionError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Rekizisaun “{r.request_no}” kansela ona.")
    return redirect("requisitions:requisition_detail", pk=pk)