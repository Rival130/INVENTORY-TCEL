# products/views.py  (aumenta iha ikus; import iha leten)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import WarehouseForm
from .models import Warehouse


@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.select_related("manager").order_by("name")
    return render(request, "warehouse/warehouse_list.html", {"warehouses": warehouses})


@login_required
def warehouse_create(request):
    form = WarehouseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        warehouse = form.save()
        messages.success(request, f"Armazén “{warehouse.name}” aumenta ona ho susesu.")
        return redirect("warehouse:warehouse_list")
    return render(request, "warehouse/warehouse_form.html", {
        "form": form,
        "title": "Aumenta Armazén",
    })


@login_required
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    form = WarehouseForm(request.POST or None, instance=warehouse)
    if request.method == "POST" and form.is_valid():
        warehouse = form.save()
        messages.success(request, f"Armazén “{warehouse.name}” atualiza ona ho susesu.")
        return redirect("warehouse:warehouse_list")
    return render(request, "warehouse/warehouse_form.html", {
        "form": form,
        "title": "Edita Armazén",
    })


@login_required
@require_POST
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    name = warehouse.name
    try:
        warehouse.delete()
        messages.success(request, f"Armazén “{name}” hamoos ona.")
    except ProtectedError:
        messages.error(
            request,
            f"Armazén “{name}” la bele hamoos tanba iha dadus stock/movimentu ne'ebé relasiona. "
            "Troka status ba “La Ativu” hodi taka armazén ne'e.",
        )
    return redirect("warehouse:warehouse_list")