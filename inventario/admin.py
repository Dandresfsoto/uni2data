from django.contrib import admin

from inventario.models import Productos, CargarProductos, Adiciones, Despachos, Sustracciones

admin.site.register(Productos)
admin.site.register(CargarProductos)
admin.site.register(Adiciones)
admin.site.register(Despachos)
admin.site.register(Sustracciones)
