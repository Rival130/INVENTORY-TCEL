# modules/reports/views.py
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Max
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from modules.purchases.models import Purchase
from modules.stock.models import Stock, StockMovement
from modules.stock.services import signed_delta

from .forms import ReportFilterForm
from .models import PriceHistory, StockSnapshot
from .services import take_snapshot

NUM = "text-end pl-num"


# ---------- Helper ----------
def _c(text, order=None, cls=""):
    """Sel tabela: text = hatudu, order = valór ba sort (default = text)."""
    return {"text": text, "order": text if order is None else order, "cls": cls}


def _money(v):
    return f"${v:,.2f}"


def _filters(request, defaults=None):
    """Foti filtru husi GET. defaults = valór default se parameter la iha (vizita dahuluk)."""
    data = request.GET.copy()
    for key, value in (defaults or {}).items():
        if key not in data:
            data[key] = value
    form = ReportFilterForm(data if data else None)
    cleaned = form.cleaned_data if form.is_bound and form.is_valid() else {}
    return form, cleaned


def _render(request, *, title, subtitle, form, field_names, columns, rows, summary,
            order_col=0, order_dir="asc", notice=""):
    return render(request, "reports/report_table.html", {
        "title": title,
        "subtitle": subtitle,
        "form": form,
        "fields": [form[n] for n in field_names],
        "columns": columns,
        "rows": rows,
        "summary": summary,
        "order_col": order_col,
        "order_dir": order_dir,
        "notice": notice,
    })


# ---------- Índise ----------
@login_required
def report_index(request):
    last = StockSnapshot.objects.aggregate(d=Max("date"))["d"]
    return render(request, "reports/report_index.html", {
        "last_snapshot": last,
        "snapshot_rows": StockSnapshot.objects.filter(date=last).count() if last else 0,
        "can_snapshot": request.user.is_staff,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def snapshot_now(request):
    day, count = take_snapshot()
    messages.success(request, f"Snapshot {day:%d/%m/%Y} rai ona ({count} liña stock).")
    return redirect("reports:index")


# ---------- 1. Relatóriu Stock ----------
@login_required
def stock_report(request):
    form, f = _filters(request)
    today = timezone.localdate()
    as_of = f.get("as_of")
    notice = ""
    rows = []
    qty_total = value_total = low = 0

    def build(product, warehouse, qty, cost):
        value = qty * cost
        is_low = qty <= (product.min_stock or 0)
        cat = product.category.name if product.category else "—"
        return [
            _c(product.name),
            _c(getattr(product, "sku", "") or "—"),
            _c(cat),
            _c(warehouse.name),
            _c(str(qty), qty, NUM),
            _c(_money(cost), float(cost), NUM),
            _c(_money(value), float(value), NUM),
            _c("Stock ki'ik" if is_low else "Normal"),
        ], value, is_low

    if as_of and as_of < today:
        snap_date = StockSnapshot.objects.filter(date__lte=as_of).aggregate(d=Max("date"))["d"]
        if snap_date is None:
            notice = "Seidauk iha snapshot to'o data ne'e. Foti snapshot iha pájina Relatóriu."
        else:
            if snap_date != as_of:
                notice = (f"La iha snapshot ba {as_of:%d/%m/%Y}. Uza snapshot besik liu: {snap_date:%d/%m/%Y}.")
            qs = StockSnapshot.objects.filter(date=snap_date).select_related("product__category", "warehouse")
            if f.get("warehouse"): qs = qs.filter(warehouse=f["warehouse"])
            if f.get("category"): qs = qs.filter(product__category=f["category"])
            if f.get("product"): qs = qs.filter(product=f["product"])
            for s in qs.order_by("product__name", "warehouse__name"):
                row, value, is_low = build(s.product, s.warehouse, s.quantity, s.unit_cost)
                rows.append(row); qty_total += s.quantity; value_total += value; low += is_low
    else:
        qs = Stock.objects.select_related("product__category", "warehouse")
        if f.get("warehouse"): qs = qs.filter(warehouse=f["warehouse"])
        if f.get("category"): qs = qs.filter(product__category=f["category"])
        if f.get("product"): qs = qs.filter(product=f["product"])
        for s in qs.order_by("product__name", "warehouse__name"):
            row, value, is_low = build(s.product, s.warehouse, s.quantity, s.product.purchase_price)
            rows.append(row); qty_total += s.quantity; value_total += value; low += is_low

    return _render(
        request,
        title="Relatóriu Stock",
        subtitle="Kuantidade no valór stock iha armazén (folin sosa).",
        form=form, field_names=["as_of", "warehouse", "category", "product"],
        columns=[("Produtu", ""), ("SKU", ""), ("Kategoria", ""), ("Armazén", ""),
                 ("Kuantidade", NUM), ("Folin Sosa", NUM), ("Valór Stock", NUM), ("Status", "")],
        rows=rows,
        summary=[("Liña", len(rows)), ("Total kuantidade", f"{qty_total:,}"),
                 ("Stock ki'ik", low), ("Valór stock", _money(value_total))],
        order_col=0, notice=notice,
    )


# ---------- 2. Relatóriu Movimentu ----------
@login_required
def movement_report(request):
    today = timezone.localdate()
    form, f = _filters(request, defaults={
        "date_from": (today - timedelta(days=30)).isoformat(),
        "date_to": today.isoformat(),
    })
    qs = StockMovement.objects.select_related("product", "warehouse", "created_by")
    if f.get("date_from"): qs = qs.filter(created_at__date__gte=f["date_from"])
    if f.get("date_to"): qs = qs.filter(created_at__date__lte=f["date_to"])
    if f.get("warehouse"): qs = qs.filter(warehouse=f["warehouse"])
    if f.get("product"): qs = qs.filter(product=f["product"])
    if f.get("movement_type"): qs = qs.filter(movement_type=f["movement_type"])

    labels = {"in": "Tama", "out": "Sai", "adjust": "Ajustamentu"}
    rows, total_in, total_out = [], 0, 0
    for m in qs.order_by("-created_at"):
        delta = signed_delta(m.movement_type, m.quantity)
        total_in += delta if delta > 0 else 0
        total_out += -delta if delta < 0 else 0
        when = timezone.localtime(m.created_at)
        user = (m.created_by.get_full_name() or m.created_by.get_username()) if m.created_by else "—"
        rows.append([
            _c(when.strftime("%d/%m/%Y %H:%M"), when.strftime("%Y-%m-%d %H:%M")),
            _c(m.product.name), _c(m.warehouse.name),
            _c(labels.get(m.movement_type, m.movement_type)),
            _c(f"{delta:+d}", delta, NUM),
            _c(m.reference or "—"), _c(user),
        ])

    return _render(
        request,
        title="Relatóriu Movimentu Stock",
        subtitle="Tama, sai no ajustamentu iha períodu ne'ebé hili.",
        form=form, field_names=["date_from", "date_to", "warehouse", "product", "movement_type"],
        columns=[("Data", ""), ("Produtu", ""), ("Armazén", ""), ("Tipu", ""),
                 ("Kuantidade", NUM), ("Referénsia", ""), ("Utilizadór", "")],
        rows=rows,
        summary=[("Movimentu", len(rows)), ("Total tama", f"{total_in:,}"), ("Total sai", f"{total_out:,}")],
        order_col=0, order_dir="desc",
    )


# ---------- 3. Relatóriu Sosa ----------
@login_required
def purchase_report(request):
    today = timezone.localdate()
    form, f = _filters(request, defaults={
        "date_from": today.replace(day=1).isoformat(),
        "date_to": today.isoformat(),
    })
    qs = Purchase.objects.select_related("supplier", "warehouse").prefetch_related("items")
    if f.get("date_from"): qs = qs.filter(date__gte=f["date_from"])
    if f.get("date_to"): qs = qs.filter(date__lte=f["date_to"])
    if f.get("supplier"): qs = qs.filter(supplier=f["supplier"])
    if f.get("warehouse"): qs = qs.filter(warehouse=f["warehouse"])
    if f.get("status"): qs = qs.filter(status=f["status"])

    labels = {"pending": "Pendente", "received": "Simu ona", "cancelled": "Kansela"}
    rows, total_value, received_value, pending = [], 0, 0, 0
    for p in qs.order_by("-date", "-id"):
        items = list(p.items.all())
        total = sum(i.subtotal for i in items)
        if p.status != "cancelled": total_value += total
        if p.status == "received": received_value += total
        if p.status == "pending": pending += 1
        rows.append([
            _c(p.invoice_no), _c(p.supplier.name), _c(p.warehouse.name),
            _c(p.date.strftime("%d/%m/%Y"), p.date.isoformat()),
            _c(labels.get(p.status, p.status)),
            _c(str(len(items)), len(items), NUM),
            _c(_money(total), float(total), NUM),
        ])

    return _render(
        request,
        title="Relatóriu Sosa",
        subtitle="Sosa husi fornesedór iha períodu ne'ebé hili.",
        form=form, field_names=["date_from", "date_to", "supplier", "warehouse", "status"],
        columns=[("Fatura", ""), ("Fornesedór", ""), ("Armazén", ""), ("Data", ""),
                 ("Status", ""), ("Item", NUM), ("Total", NUM)],
        rows=rows,
        summary=[("Sosa", len(rows)), ("Pendente", pending),
                 ("Valór total (la inklui kansela)", _money(total_value)),
                 ("Valór simu ona", _money(received_value))],
        order_col=3, order_dir="desc",
    )


# ---------- 4. Istória Folin ----------
@login_required
def price_history_report(request):
    form, f = _filters(request)
    qs = PriceHistory.objects.select_related("product", "changed_by")
    if f.get("date_from"): qs = qs.filter(changed_at__date__gte=f["date_from"])
    if f.get("date_to"): qs = qs.filter(changed_at__date__lte=f["date_to"])
    if f.get("product"): qs = qs.filter(product=f["product"])

    rows = []
    for h in qs.order_by("-changed_at", "-id"):
        when = timezone.localtime(h.changed_at)
        margin = h.margin_percent
        user = (h.changed_by.get_full_name() or h.changed_by.get_username()) if h.changed_by else "—"
        rows.append([
            _c(when.strftime("%d/%m/%Y %H:%M"), when.strftime("%Y-%m-%d %H:%M")),
            _c(h.product.name),
            _c(_money(h.purchase_price), float(h.purchase_price), NUM),
            _c(_money(h.selling_price), float(h.selling_price), NUM),
            _c(f"{margin:.1f}%" if margin is not None else "—", float(margin) if margin is not None else -1e9, NUM),
            _c(user),
        ])

    return _render(
        request,
        title="Istória Folin Produtu",
        subtitle="Rekordu kada bainhira folin sosa ka faan muda.",
        form=form, field_names=["date_from", "date_to", "product"],
        columns=[("Data", ""), ("Produtu", ""), ("Folin Sosa", NUM), ("Folin Faan", NUM),
                 ("Margen", NUM), ("Muda husi", "")],
        rows=rows,
        summary=[("Mudansa", len(rows))],
        order_col=0, order_dir="desc",
    )