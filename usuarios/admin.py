from django.contrib import admin
from usuarios.models import Departamentos, Municipios, ComunidadesProyectosIraca, ConsejosResguardosProyectosIraca
# Register your models here.

admin.site.register(Departamentos)
admin.site.register(Municipios)
admin.site.register(ComunidadesProyectosIraca)
admin.site.register(ConsejosResguardosProyectosIraca)
