from django.contrib import admin

from inventario.models import Productos, CargarProductos, Adiciones

admin.site.register(Productos)
admin.site.register(CargarProductos)
admin.site.register(Adiciones)
