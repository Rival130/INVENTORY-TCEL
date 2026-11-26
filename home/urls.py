from django.contrib import admin
from django.urls import include, path
import home.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', home.views.index, name='index'),
    path('', home.views.login, name='login'),
    path('products/', include('modules.products.urls')),
    path('categories/', include('modules.categories.urls')),  # Adiciona as URLs de categorias
    path('warehouses/', include('modules.warehouse.urls')),  # Adiciona as URLs de armazéns
    path('stock/', include('modules.stock.urls')),  # Adiciona as URLs de stock
    path('suppliers/', include('modules.suppliers.urls')),  # Adiciona as URLs de fornecedores
    path('purchases/', include('modules.purchases.urls')),  # Adiciona as URLs de compras
    path('reports/', include('modules.reports.urls')),  # Adiciona as URLs de relatórios
    path('requests/', include('modules.requisitions.urls')),  # Adiciona as URLs de requisições
]
