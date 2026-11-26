# modules/purchases/forms.py
from datetime import date

from django import forms
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from modules.products.models import Product
from modules.suppliers.models import Supplier
from modules.warehouse.models import Warehouse

from .models import Purchase, PurchaseItem


class ProductSelect(forms.Select):
    """Select produtu ho data-price (folin sosa) ba JS prense automátiku."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        instance = getattr(value, "instance", None)
        if instance is not None:
            price = getattr(instance, "purchase_price", None)
            if price is not None:
                option["attrs"]["data-price"] = str(price)
        return option


def _product_label(p):
    sku = getattr(p, "sku", "")
    return f"{p.name} · {sku}" if sku else p.name


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["invoice_no", "supplier", "warehouse", "date", "note"]
        labels = {
            "invoice_no": "Numeru Fatura",
            "supplier": "Fornesedór",
            "warehouse": "Armazén",
            "date": "Data",
            "note": "Nota",
        }
        widgets = {
            "invoice_no": forms.TextInput(attrs={"placeholder": "Ezemplu: INV-2026-001", "autofocus": True, "maxlength": 50}),
            "supplier": forms.Select(),
            "warehouse": forms.Select(),
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "note": forms.Textarea(attrs={"rows": 3, "placeholder": "Nota adisionál (opsionál)"}),
        }
        error_messages = {
            "invoice_no": {
                "required": "Numeru fatura tenke prense.",
                "unique": "Numeru fatura ida-ne'e existe ona.",
            },
            "date": {"required": "Data tenke prense.", "invalid": "Formatu data la loos."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sup_cond, wh_cond = Q(is_active=True), Q(is_active=True)
        if self.instance.pk:
            sup_cond |= Q(pk=self.instance.supplier_id)
            wh_cond |= Q(pk=self.instance.warehouse_id)

        self.fields["supplier"].queryset = Supplier.objects.filter(sup_cond).order_by("name")
        self.fields["supplier"].empty_label = "— Hili fornesedór —"
        self.fields["warehouse"].queryset = Warehouse.objects.filter(wh_cond).order_by("name")
        self.fields["warehouse"].empty_label = "— Hili armazén —"

        if not self.instance.pk:
            self.fields["date"].initial = date.today()

    def clean_invoice_no(self):
        invoice = " ".join(self.cleaned_data["invoice_no"].split())
        qs = Purchase.objects.filter(invoice_no__iexact=invoice)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Numeru fatura ida-ne'e existe ona.")
        return invoice


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "product": ProductSelect(),
            "quantity": forms.NumberInput(attrs={"min": 1, "step": 1, "placeholder": "0"}),
            "unit_price": forms.NumberInput(attrs={"min": 0, "step": "0.01", "placeholder": "0.00"}),
        }
        error_messages = {
            "product": {"required": "Hili produtu."},
            "quantity": {"required": "Prense kuantidade.", "invalid": "Kuantidade la loos."},
            "unit_price": {"required": "Prense folin.", "invalid": "Folin la loos."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cond = Q(is_active=True)
        if self.instance.pk:
            cond |= Q(pk=self.instance.product_id)
        field = self.fields["product"]
        field.queryset = Product.objects.filter(cond).order_by("name")
        field.empty_label = "— Hili produtu —"
        field.label_from_instance = _product_label

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty < 1:
            raise forms.ValidationError("Kuantidade tenke boot liu 0.")
        return qty

    def clean_unit_price(self):
        price = self.cleaned_data["unit_price"]
        if price < 0:
            raise forms.ValidationError("Folin la bele negativu.")
        return price


class BasePurchaseItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        seen, count = set(), 0
        for form in self.forms:
            cd = getattr(form, "cleaned_data", None)
            if not cd or cd.get("DELETE"):
                continue
            product = cd.get("product")
            if product is None:
                continue
            count += 1
            if product.pk in seen:
                raise forms.ValidationError(
                    f"Produtu “{product.name}” aumenta dala rua. Hamutuk kuantidade iha liña ida de'it."
                )
            seen.add(product.pk)

        if count == 0:
            raise forms.ValidationError("Aumenta ao menus produtu ida iha sosa ne'e.")


# extra=1 ba kria foun, extra=0 ba edita
PurchaseItemFormSet = inlineformset_factory(
    Purchase, PurchaseItem,
    form=PurchaseItemForm, formset=BasePurchaseItemFormSet,
    extra=1, can_delete=True,
)
PurchaseItemEditFormSet = inlineformset_factory(
    Purchase, PurchaseItem,
    form=PurchaseItemForm, formset=BasePurchaseItemFormSet,
    extra=0, can_delete=True,
)