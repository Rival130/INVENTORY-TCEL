from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Stock, StockMovement
from .services import apply_movement


class StockForm(forms.ModelForm):
    note = forms.CharField(
        label="Nota",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Stock
        fields = ["product", "warehouse", "quantity"]
        labels = {
            "product": "Produtu",
            "warehouse": "Armazén",
            "quantity": "Kuantidade",
        }
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["product"].disabled = True
            self.fields["warehouse"].disabled = True

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity < 0:
            raise forms.ValidationError("Kuantidade labele negativu.")
        return quantity

    @transaction.atomic
    def save(self, user=None, commit=True):
        stock = super().save(commit=False)
        if not commit:
            return stock

        quantity = self.cleaned_data["quantity"]
        note = self.cleaned_data.get("note", "")

        if self.instance.pk:
            stock = Stock.objects.select_for_update().get(pk=self.instance.pk)
            delta = quantity - stock.quantity
            if delta:
                apply_movement(
                    product=stock.product,
                    warehouse=stock.warehouse,
                    movement_type="adjust",
                    quantity=delta,
                    user=user,
                    note=note,
                )
        else:
            stock, created = Stock.objects.get_or_create(
                product=stock.product,
                warehouse=stock.warehouse,
                defaults={"quantity": 0},
            )
            if not created:
                raise ValidationError("Stock ba produtu no armazén ida-ne'e existe ona.")
            if quantity:
                apply_movement(
                    product=stock.product,
                    warehouse=stock.warehouse,
                    movement_type="adjust",
                    quantity=quantity,
                    user=user,
                    note=note,
                )

        stock.refresh_from_db()
        self.instance = stock
        return stock


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "movement_type",
            "product",
            "warehouse",
            "quantity",
            "reference",
            "note",
        ]
        labels = {
            "movement_type": "Tipu Movimentu",
            "product": "Produtu",
            "warehouse": "Armazén",
            "quantity": "Kuantidade",
            "reference": "Referénsia",
            "note": "Nota",
        }
        widgets = {
            "movement_type": forms.RadioSelect(),
            "quantity": forms.NumberInput(attrs={"step": 1}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get("movement_type")
        quantity = cleaned_data.get("quantity")

        if quantity is not None:
            if movement_type in {"in", "out"} and quantity <= 0:
                self.add_error("quantity", "Kuantidade tenke boot liu 0.")
            elif movement_type == "adjust" and quantity == 0:
                self.add_error("quantity", "Ajustamentu tenke la'ós 0.")

        return cleaned_data

    def save(self, user=None, commit=True):
        movement = super().save(commit=False)
        if not commit:
            return movement

        return apply_movement(
            product=movement.product,
            warehouse=movement.warehouse,
            movement_type=movement.movement_type,
            quantity=movement.quantity,
            user=user,
            reference=movement.reference,
            note=movement.note,
        )