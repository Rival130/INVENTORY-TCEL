# modules/suppliers/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SupplierForm
from .models import Supplier


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()  # Meta.ordering = ["name"]
    return render(request, "suppliers/suppliers_list.html", {"suppliers": suppliers})


@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        supplier = form.save()
        messages.success(request, f"Fornesedór “{supplier.name}” aumenta ona ho susesu.")
        return redirect("suppliers:supplier_list")
    return render(request, "suppliers/suppliers_form.html", {
        "form": form,
        "title": "Aumenta Fornesedór",
    })


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=supplier)
    if request.method == "POST" and form.is_valid():
        supplier = form.save()
        messages.success(request, f"Fornesedór “{supplier.name}” atualiza ona ho susesu.")
        return redirect("suppliers:supplier_list")
    return render(request, "suppliers/suppliers_form.html", {
        "form": form,
        "title": "Edita Fornesedór",
    })


@login_required
@require_POST
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    name = supplier.name
    try:
        supplier.delete()
        messages.success(request, f"Fornesedór “{name}” hamoos ona.")
    except ProtectedError:
        messages.error(
            request,
            f"Fornesedór “{name}” la bele hamoos tanba iha dadus sosa ne'ebé relasiona. "
            "Troka status ba “La Ativu” hodi taka fornesedór ne'e.",
        )
    return redirect("suppliers:supplier_list")