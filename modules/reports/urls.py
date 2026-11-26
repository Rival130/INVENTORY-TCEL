# modules/reports/urls.py
from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_index, name="index"),
    path("stock/", views.stock_report, name="stock"),
    path("movements/", views.movement_report, name="movements"),
    path("purchases/", views.purchase_report, name="purchases"),
    path("prices/", views.price_history_report, name="prices"),
    path("snapshot/", views.snapshot_now, name="snapshot"),
]

# Iha config/urls.py:
# path("reports/", include("modules.reports.urls")),