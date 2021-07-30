from django.contrib import admin
from fest_2020_ import models
import openpyxl
from usuarios.models import Municipios
# Register your models here.
admin.site.register(models.Componentes)
admin.site.register(models.Momentos)
admin.site.register(models.Instrumentos)
admin.site.register(models.CuposRutaObject)
admin.site.register(models.Categoria)
admin.site.register(models.Productos)
admin.site.register(models.Hogares)
admin.site.register(models.CuentasCobro)
admin.site.register(models.Cortes)
admin.site.register(models.Liquidaciones)


def actualizar_hogares(modeladmin, request, queryset):

    for data in queryset:
        wb = openpyxl.load_workbook(data.file)
        ws = wb.get_active_sheet()

        for file in ws.rows:

            if models.Hogares.objects.filter(documento=file[1].value).count() == 0:
                models.Hogares.objects.create(
                    documento=file[1].value,
                    primer_apellido = file[2].value,
                    segundo_apellido = file[3].value,
                    primer_nombre = file[4].value,
                    segundo_nombre = file[5].value,
                    fecha_nacimiento=file[6].value,
                    municipio=Municipios.objects.get(codigo = file[7].value),
                    municipio_residencia=Municipios.objects.get(codigo = file[8].value),
                )


class CargaMasivaHogaresAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_hogares]
admin.site.register(models.CargaMasivaHogares, CargaMasivaHogaresAdmin)