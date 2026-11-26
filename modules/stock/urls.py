# modules/stock/urls.py
from django.urls import path

from . import views

app_name = "stock"

urlpatterns = [
    # Stock
    path("", views.stock_list, name="stock_list"),
    path("create/", views.stock_create, name="stock_create"),
    path("<int:pk>/update/", views.stock_update, name="stock_update"),
    path("<int:pk>/delete/", views.stock_delete, name="stock_delete"),

    # Movimentu
    path("movements/", views.movement_list, name="movement_list"),
    path("movements/create/", views.movement_create, name="movement_create"),

    # JSON: stock atuál
    path("quantity/", views.stock_quantity, name="quantity"),
]

# Iha config/urls.py:
# path("stock/", include("modules.stock.urls")),