# products/views.py  (aumenta iha ikus; import iha leten)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CategoryForm
from .models import Category


@login_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count("products"))
    return render(request, "categories/categories_list.html", {"categories": categories})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Kategoria “{category.name}” aumenta ona ho susesu.")
        return redirect("categories:category_list")
    return render(request, "categories/categories_form.html", {
        "form": form,
        "title": "Aumenta Kategoria",
    })


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Kategoria “{category.name}” atualiza ona ho susesu.")
        return redirect("categories:category_list")
    return render(request, "categories/categories_form.html", {
        "form": form,
        "title": "Edita Kategoria",
    })


@login_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    try:
        category.delete()
        messages.success(request, f"Kategoria “{name}” hamoos ona.")
    except ProtectedError:
        messages.error(request, f"Kategoria “{name}” la bele hamoos tanba seidauk hasai produtu sira ne'ebé uza kategoria ne'e.")
    return redirect("categories:category_list")