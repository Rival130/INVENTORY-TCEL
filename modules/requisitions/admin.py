from django.contrib import admin

from modules.requisitions.models import Requisition, RequisitionItem


# Register your models here.
admin.site.register(Requisition)
admin.site.register(RequisitionItem)



