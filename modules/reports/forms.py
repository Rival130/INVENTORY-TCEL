# modules/reports/forms.py
from django import forms

from modules.products.models import Product
from modules.suppliers.models import Supplier
from modules.warehouse.models import Warehouse

# Category model: la presiza import diretu (path sira bele diferente), foti husi Product.category
Category = Product._meta.get_field("category").related_model

DATE_WIDGET = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")

MOVEMENT_TYPES = [("", "Hotu"), ("in", "Tama"), ("out", "Sai"), ("adjust", "Ajustamentu")]
PURCHASE_STATUS = [("", "Hotu"), ("pending", "Pendente"), ("received", "Simu ona"), ("cancelled", "Kansela")]


class ReportFilterForm(forms.Form):
    """Filtru jerál ba relatóriu. Relatóriu ida-idak hatudu de'it kampu ne'ebé relevante."""

    as_of = forms.DateField(label="Stock iha data", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    date_from = forms.DateField(label="Husi data", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    date_to = forms.DateField(label="To'o data", required=False, widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    warehouse = forms.ModelChoiceField(label="Armazén", queryset=Warehouse.objects.none(), required=False, empty_label="Hotu")
    supplier = forms.ModelChoiceField(label="Fornesedór", queryset=Supplier.objects.none(), required=False, empty_label="Hotu")
    category = forms.ModelChoiceField(label="Kategoria", queryset=Category.objects.none(), required=False, empty_label="Hotu")
    product = forms.ModelChoiceField(label="Produtu", queryset=Product.objects.none(), required=False, empty_label="Hotu")
    movement_type = forms.ChoiceField(label="Tipu Movimentu", choices=MOVEMENT_TYPES, required=False)
    status = forms.ChoiceField(label="Status", choices=PURCHASE_STATUS, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["warehouse"].queryset = Warehouse.objects.order_by("name")
        self.fields["supplier"].queryset = Supplier.objects.order_by("name")
        self.fields["category"].queryset = Category.objects.order_by("name")
        self.fields["product"].queryset = Product.objects.order_by("name")

    def clean(self):
        cleaned = super().clean()
        d1, d2 = cleaned.get("date_from"), cleaned.get("date_to")
        if d1 and d2 and d1 > d2:
            self.add_error("date_to", "Data to'o tenke depois data husi.")
        return cleaned