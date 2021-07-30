from django.contrib import admin
from formacion.models import Diplomados, Niveles, Sesiones, Sedes, Actividades

# Register your models here.

admin.site.register(Diplomados)
admin.site.register(Niveles)
admin.site.register(Sesiones)
admin.site.register(Sedes)
admin.site.register(Actividades)
