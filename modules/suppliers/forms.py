# modules/suppliers/forms.py
import re

from django import forms

from .models import Supplier

PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-()]{5,18}$")


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "phone", "email", "address", "is_active"]
        labels = {
            "name": "Naran Fornesedór",
            "contact_person": "Pesoa Kontaktu",
            "phone": "Telefone",
            "email": "Email",
            "address": "Enderesu",
            "is_active": "Ativu",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ezemplu: PT. Timor Distribuidór",
                "autofocus": True,
                "maxlength": 150,
            }),
            "contact_person": forms.TextInput(attrs={"placeholder": "Naran pesoa kontaktu", "maxlength": 100}),
            "phone": forms.TextInput(attrs={
                "type": "tel",
                "inputmode": "tel",
                "placeholder": "+670 7700 0000",
                "maxlength": 20,
                "autocomplete": "off",
            }),
            "email": forms.EmailInput(attrs={"placeholder": "naran@ezemplu.com", "autocomplete": "off"}),
            "address": forms.Textarea(attrs={"rows": 3, "placeholder": "Enderesu kompletu"}),
            "is_active": forms.CheckboxInput(),
        }
        error_messages = {
            "name": {
                "required": "Naran fornesedór tenke prense.",
                "max_length": "Naran naruk liu (maksimu karakter 150).",
            },
            "phone": {"max_length": "Númeru telefone naruk liu (maksimu karakter 20)."},
            "email": {"invalid": "Formatu email la loos."},
        }

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        # Naran la úniku iha model (database), maibé form ne'e bloka naran hanesan atu evita duplikadu.
        # Se ita-boot hakarak permite naran hanesan, hasai bloku ida-ne'e.
        qs = Supplier.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Fornesedór ho naran ida-ne'e existe ona.")
        return name

    def clean_contact_person(self):
        return " ".join(self.cleaned_data.get("contact_person", "").split())

    def clean_phone(self):
        phone = " ".join(self.cleaned_data.get("phone", "").split())
        if phone and not PHONE_RE.match(phone):
            raise forms.ValidationError("Númeru telefone la loos. Uza de'it númeru, espasu, +, - no ( ).")
        return phone

    def clean_email(self):
        return self.cleaned_data.get("email", "").strip().lower()

    def clean_address(self):
        return self.cleaned_data.get("address", "").strip()