# warehouse/urls.py  (aumenta iha laran urlpatterns; app_name = "warehouse" tenke iha ona)
from django.urls import path
from . import views

app_name = "warehouse"

urlpatterns = [
    # ... URL armazém ne'ebé iha ona ...

    path("", views.warehouse_list, name="warehouse_list"),
    path("create/", views.warehouse_create, name="warehouse_create"),
    path("<int:pk>/update/", views.warehouse_update, name="warehouse_update"),
    path("<int:pk>/delete/", views.warehouse_delete, name="warehouse_delete"),
]
