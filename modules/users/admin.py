from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "phone")

    # Aumenta field foun (role, phone) iha form edit
    fieldsets = UserAdmin.fieldsets + (
        ("Informasaun Adisionál", {"fields": ("role", "phone")}),
    )
    # Aumenta field foun iha form kria user foun
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informasaun Adisionál", {"fields": ("role", "phone")}),
    )