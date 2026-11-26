# modules/stock/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import StockForm, StockMovementForm
from .models import Stock, StockMovement
from .services import InsufficientStock, signed_delta


# ---------- Stock ----------
@login_required
def stock_list(request):
    stocks = list(
        Stock.objects.select_related("product", "warehouse")
        .order_by("product__name", "warehouse__name")
    )
    for s in stocks:
        # Stock ki'ik = kuantidade ≤ stock minimu produtu nian
        s.is_low = s.quantity <= (s.product.min_stock or 0)
    return render(request, "stock/stock_list.html", {"stocks": stocks})


@login_required
def stock_create(request):
    form = StockForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            stock = form.save(user=request.user)
        except InsufficientStock as e:
            form.add_error("quantity", str(e))
        else:
            messages.success(request, f"Stock “{stock.product}” iha “{stock.warehouse}” rai ona.")
            return redirect("stock:stock_list")
    return render(request, "stock/stock_form.html", {"form": form, "title": "Aumenta Stock"})


@login_required
def stock_update(request, pk):
    stock = get_object_or_404(Stock.objects.select_related("product", "warehouse"), pk=pk)
    form = StockForm(request.POST or None, instance=stock)
    if request.method == "POST" and form.is_valid():
        try:
            stock = form.save(user=request.user)
        except InsufficientStock as e:
            form.add_error("quantity", str(e))
        else:
            messages.success(request, f"Stock “{stock.product}” iha “{stock.warehouse}” atualiza ona.")
            return redirect("stock:stock_list")
    return render(request, "stock/stock_form.html", {"form": form, "title": "Edita Stock"})


@login_required
@require_POST
def stock_delete(request, pk):
    stock = get_object_or_404(Stock.objects.select_related("product", "warehouse"), pk=pk)
    label = f"{stock.product} @ {stock.warehouse}"
    if stock.quantity != 0:
        messages.error(
            request,
            f"Stock “{label}” seidauk 0 (kuantidade: {stock.quantity}). "
            "Halo movimentu “Sai” ka “Ajustamentu” to'o 0 molok hamoos.",
        )
    else:
        stock.delete()
        messages.success(request, f"Stock “{label}” hamoos ona.")
    return redirect("stock:stock_list")


# ---------- Movimentu ----------
@login_required
def movement_list(request):
    movements = list(
        StockMovement.objects.select_related("product", "warehouse", "created_by")
        .order_by("-created_at")
    )
    for m in movements:
        m.delta = signed_delta(m.movement_type, m.quantity)
    return render(request, "stock/stock_movement_list.html", {"movements": movements})


@login_required
def movement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                movement = form.save(user=request.user)
            except InsufficientStock as e:
                form.add_error("quantity", str(e))
            else:
                messages.success(
                    request,
                    f"Movimentu “{movement.get_movement_type_display()}” ba {movement.product} rai ona.",
                )
                return redirect("stock:movement_list")
    else:
        # Prefill husi botaun iha lista stock: ?product=ID&warehouse=ID
        initial = {k: request.GET[k] for k in ("product", "warehouse") if request.GET.get(k, "").isdigit()}
        form = StockMovementForm(initial=initial)
    return render(request, "stock/stock_movement_form.html", {"form": form, "title": "Movimentu Stock Foun"})


# ---------- JSON: stock atuál (ba formuláriu movimentu) ----------
@login_required
@require_GET
def stock_quantity(request):
    product_id = request.GET.get("product", "")
    warehouse_id = request.GET.get("warehouse", "")
    if not (product_id.isdigit() and warehouse_id.isdigit()):
        return JsonResponse({"quantity": 0, "unit": ""}, status=400)

    row = (
        Stock.objects.filter(product_id=product_id, warehouse_id=warehouse_id)
        .values("quantity", unit=F("product__unit"))
        .first()
    )
    if row is None:
        from modules.products.models import Product
        unit = Product.objects.filter(pk=product_id).values_list("unit", flat=True).first() or ""
        return JsonResponse({"quantity": 0, "unit": unit})
    return JsonResponse({"quantity": row["quantity"], "unit": row["unit"] or ""})