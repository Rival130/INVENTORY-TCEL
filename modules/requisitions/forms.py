# modules/requisitions/forms.py
from datetime import date

from django import forms
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory

from modules.products.models import Product
from modules.warehouse.models import Warehouse

from .models import Requisition, RequisitionItem


def _product_label(p):
    sku = getattr(p, "sku", "")
    return f"{p.name} · {sku}" if sku else p.name


class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Requisition
        fields = ["warehouse", "department", "needed_date", "priority", "purpose"]
        labels = {
            "warehouse": "Armazén (fatin foti sasán)",
            "department": "Departamentu / Unidade",
            "needed_date": "Data presiza",
            "priority": "Prioridade",
            "purpose": "Razaun / Objetivu",
        }
        widgets = {
            "warehouse": forms.Select(),
            "department": forms.TextInput(attrs={"placeholder": "Ezemplu: Administrasaun", "maxlength": 100}),
            "needed_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "priority": forms.Select(choices=[("normal", "Normal"), ("urgent", "Urjente")]),
            "purpose": forms.Textarea(attrs={"rows": 3, "placeholder": "Tansá presiza sasán sira ne'e? (opsionál)"}),
        }
        error_messages = {
            "warehouse": {"required": "Hili armazén."},
            "needed_date": {"invalid": "Formatu data la loos."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cond = Q(is_active=True)
        if self.instance.pk:
            cond |= Q(pk=self.instance.warehouse_id)
        wh = self.fields["warehouse"]
        wh.queryset = Warehouse.objects.filter(cond).order_by("name")
        wh.empty_label = "— Hili armazén —"

    def clean_needed_date(self):
        d = self.cleaned_data.get("needed_date")
        if d and not self.instance.pk and d < date.today():
            raise forms.ValidationError("Data presiza la bele iha pasadu.")
        return d

    def clean_department(self):
        return " ".join(self.cleaned_data.get("department", "").split())


class RequisitionItemForm(forms.ModelForm):
    class Meta:
        model = RequisitionItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(),
            "quantity": forms.NumberInput(attrs={"min": 1, "step": 1, "placeholder": "0"}),
        }
        error_messages = {
            "product": {"required": "Hili produtu."},
            "quantity": {"required": "Prense kuantidade.", "invalid": "Kuantidade la loos."},
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


class BaseRequisitionItemFormSet(BaseInlineFormSet):
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
            raise forms.ValidationError("Aumenta ao menus produtu ida.")


RequisitionItemFormSet = inlineformset_factory(
    Requisition, RequisitionItem,
    form=RequisitionItemForm, formset=BaseRequisitionItemFormSet,
    extra=1, can_delete=True,
)
RequisitionItemEditFormSet = inlineformset_factory(
    Requisition, RequisitionItem,
    form=RequisitionItemForm, formset=BaseRequisitionItemFormSet,
    extra=0, can_delete=True,
)