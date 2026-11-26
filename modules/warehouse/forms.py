# products/forms.py  (aumenta iha ikus; import iha leten)
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Warehouse


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "location", "manager", "is_active"]
        labels = {
            "name": "Naran Armazén",
            "location": "Lokalizasaun",
            "manager": "Manajer",
            "is_active": "Ativu",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ezemplu: Armazén Sentrál",
                "autofocus": True,
                "maxlength": 100,
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "Ezemplu: Comoro, Dili",
                "maxlength": 200,
            }),
            "manager": forms.Select(),
            "is_active": forms.CheckboxInput(),
        }
        error_messages = {
            "name": {
                "required": "Naran armazén tenke prense.",
                "max_length": "Naran naruk liu (maksimu karakter 100).",
                "unique": "Armazén ho naran ida-ne'e existe ona.",
            },
            "location": {"max_length": "Lokalizasaun naruk liu (maksimu karakter 200)."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()

        # Utilizadór ativu de'it; mantén manajer atuál mesmu se nia la ativu ona
        condition = Q(is_active=True)
        if self.instance.pk and self.instance.manager_id:
            condition |= Q(pk=self.instance.manager_id)

        manager = self.fields["manager"]
        manager.queryset = User.objects.filter(condition).order_by("username")
        manager.empty_label = "— La iha manajer —"
        manager.label_from_instance = lambda u: u.get_full_name() or u.get_username()

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())

        qs = Warehouse.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Armazén ho naran ida-ne'e existe ona.")
        return name

    def clean_location(self):
        return " ".join(self.cleaned_data.get("location", "").split())