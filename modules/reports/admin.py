from django.contrib import admin

from modules.reports.models import PriceHistory, StockSnapshot

# Register your models here.
admin.site.register(PriceHistory)
admin.site.register(StockSnapshot)