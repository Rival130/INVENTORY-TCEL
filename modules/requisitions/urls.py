# modules/requisitions/urls.py
from django.urls import path

from . import views

app_name = "requisitions"

urlpatterns = [
    path("", views.requisition_list, name="requisition_list"),
    path("create/", views.requisition_create, name="requisition_create"),
    path("<int:pk>/", views.requisition_detail, name="requisition_detail"),
    path("<int:pk>/update/", views.requisition_update, name="requisition_update"),
    path("<int:pk>/approve/", views.requisition_approve, name="requisition_approve"),
    path("<int:pk>/reject/", views.requisition_reject, name="requisition_reject"),
    path("<int:pk>/issue/", views.requisition_issue, name="requisition_issue"),
    path("<int:pk>/cancel/", views.requisition_cancel, name="requisition_cancel"),
]

# Iha config/urls.py:
# path("requisitions/", include("modules.requisitions.urls")),