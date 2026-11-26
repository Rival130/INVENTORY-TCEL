# modules/purchases/urls.py
from django.urls import path

from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.purchase_list, name="purchase_list"),
    path("create/", views.purchase_create, name="purchase_create"),
    path("<int:pk>/", views.purchase_detail, name="purchase_detail"),
    path("<int:pk>/update/", views.purchase_update, name="purchase_update"),
    path("<int:pk>/receive/", views.purchase_receive, name="purchase_receive"),
    path("<int:pk>/cancel/", views.purchase_cancel, name="purchase_cancel"),
    path("<int:pk>/delete/", views.purchase_delete, name="purchase_delete"),
]

# Iha config/urls.py:
# path("purchases/", include("modules.purchases.urls")),