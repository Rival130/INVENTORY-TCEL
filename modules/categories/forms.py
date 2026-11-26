# products/forms.py  (aumenta iha ikus; import iha leten)
from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        labels = {
            "name": "Naran Kategoria",
            "description": "Deskrisaun",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Ezemplu: Hahan, Bebida, Eletróniku",
                "autofocus": True,
                "maxlength": 100,
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Deskrisaun badak kona-ba kategoria ne'e",
            }),
        }
        error_messages = {
            "name": {
                "required": "Naran kategoria tenke prense.",
                "max_length": "Naran naruk liu (maksimu karakter 100).",
                "unique": "Kategoria ho naran ida-ne'e existe ona.",
            }
        }

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())  # hasai espasu liu

        # Verifika naran hanesan la hanesan letra boot/ki'ik (ezemplu "Hahan" vs "hahan")
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Kategoria ho naran ida-ne'e existe ona.")
        return name