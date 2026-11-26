from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ProductForm
from .models import Product


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return (
            Product.objects.select_related("category")
            .annotate(total_stock=Coalesce(Sum("stocks__quantity"), 0))
        )


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        messages.success(self.request, "Produtu foun rai ho susesu.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Aumenta Produtu"
        return ctx


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        messages.success(self.request, "Produtu atualiza ho susesu.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edita Produtu"
        return ctx


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("products:list")
    http_method_names = ["post"]  # delete liu husi modal (POST) de'it

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Produtu hamoos ho susesu.")
        except ProtectedError:
            messages.error(
                request,
                "Produtu ne'e la bele hamoos tanba iha ona iha transasaun compra/stock. "
                "Troka status ba 'La Ativu' de'it.",
            )
        return redirect(self.success_url)