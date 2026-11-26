from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku", "name", "category", "unit",
            "purchase_price", "selling_price", "min_stock",
            "image", "description", "is_active",
        ]
        labels = {
            "sku": "SKU / Kódigu",
            "name": "Naran Produtu",
            "category": "Kategoria",
            "unit": "Unidade",
            "purchase_price": "Folin Sosa",
            "selling_price": "Folin Faan",
            "min_stock": "Stock Mínimu",
            "image": "Imajen",
            "description": "Deskrisaun",
            "is_active": "Ativu",
        }
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: PRD-001"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "unit": forms.TextInput(attrs={"class": "form-control", "placeholder": "pcs, kg, box..."}),
            "purchase_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "selling_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "min_stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "custom-control-input"}),
        }

    def clean(self):
        data = super().clean()
        buy, sell = data.get("purchase_price"), data.get("selling_price")
        if buy is not None and sell is not None and sell < buy:
            self.add_error("selling_price", "Folin faan la bele ki'ik liu folin sosa.")
        return data