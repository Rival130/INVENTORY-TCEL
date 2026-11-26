# modules/purchases/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from modules.stock.services import InsufficientStock

from .forms import PurchaseForm, PurchaseItemEditFormSet, PurchaseItemFormSet
from .models import Purchase
from .services import PurchaseError, cancel_purchase, receive_purchase


@login_required
def purchase_list(request):
    purchases = list(
        Purchase.objects.select_related("supplier", "warehouse")
        .prefetch_related("items")
    )
    for p in purchases:
        items = list(p.items.all())  # prefetch: la iha query tan
        p.item_count = len(items)
        p.grand_total = sum(i.subtotal for i in items)
    return render(request, "purchases/purchase_list.html", {"purchases": purchases})


@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(
        Purchase.objects.select_related("supplier", "warehouse", "created_by"), pk=pk
    )
    items = list(purchase.items.select_related("product"))
    total = sum(i.subtotal for i in items)
    return render(request, "purchases/purchase_detail.html", {
        "purchase": purchase,
        "items": items,
        "total": total,
    })


@login_required
def purchase_create(request):
    purchase = Purchase()
    form = PurchaseForm(request.POST or None)
    formset = PurchaseItemFormSet(request.POST or None, instance=purchase)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.save()
            formset.instance = purchase
            formset.save()
        messages.success(request, f"Sosa “{purchase.invoice_no}” rai ona. Marka “Simu Stock” bainhira sasán to'o.")
        return redirect("purchases:purchase_detail", pk=purchase.pk)

    return render(request, "purchases/purchase_form.html", {
        "form": form,
        "formset": formset,
        "title": "Sosa Foun",
    })


@login_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if purchase.status != "pending":
        messages.error(request, "Sosa ne'ebé simu ona ka kansela ona la bele edita.")
        return redirect("purchases:purchase_detail", pk=purchase.pk)

    form = PurchaseForm(request.POST or None, instance=purchase)
    formset = PurchaseItemEditFormSet(request.POST or None, instance=purchase)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            form.save()
            formset.save()
        messages.success(request, f"Sosa “{purchase.invoice_no}” atualiza ona.")
        return redirect("purchases:purchase_detail", pk=purchase.pk)

    return render(request, "purchases/purchase_form.html", {
        "form": form,
        "formset": formset,
        "title": f"Edita Sosa {purchase.invoice_no}",
    })


@login_required
@require_POST
def purchase_receive(request, pk):
    get_object_or_404(Purchase, pk=pk)
    try:
        purchase = receive_purchase(pk, user=request.user)
    except (PurchaseError, InsufficientStock) as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Sosa “{purchase.invoice_no}” simu ona. Stock atualiza ona.")
    return redirect("purchases:purchase_detail", pk=pk)


@login_required
@require_POST
def purchase_cancel(request, pk):
    get_object_or_404(Purchase, pk=pk)
    try:
        purchase = cancel_purchase(pk)
    except PurchaseError as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f"Sosa “{purchase.invoice_no}” kansela ona.")
    return redirect("purchases:purchase_detail", pk=pk)


@login_required
@require_POST
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    invoice = purchase.invoice_no
    if purchase.status == "received":
        messages.error(request, f"Sosa “{invoice}” simu ona (stock tama ona), la bele hamoos.")
        return redirect("purchases:purchase_detail", pk=pk)
    try:
        purchase.delete()
        messages.success(request, f"Sosa “{invoice}” hamoos ona.")
    except ProtectedError:
        messages.error(request, f"Sosa “{invoice}” la bele hamoos tanba iha dadus relasiona.")
    return redirect("purchases:purchase_list")