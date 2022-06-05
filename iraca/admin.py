import openpyxl
from django.contrib import admin
from usuarios.models import Municipios

from iraca import models

admin.site.register(models.Certificates)
admin.site.register(models.Moments)
admin.site.register(models.Types)
admin.site.register(models.Instruments)
admin.site.register(models.Routes)
admin.site.register(models.Resguards)
admin.site.register(models.Comunity)


def actualizar_hogares(modeladmin, request, queryset):

    for data in queryset:
        wb = openpyxl.load_workbook(data.file)
        ws = wb.active

        for file in ws.rows:

            if models.Households.objects.filter(document=file[1].value).count() == 0:
                models.Households.objects.create(
                    document=file[1].value,
                    first_surname = file[2].value,
                    second_surname = file[3].value,
                    first_name = file[4].value,
                    second_name = file[5].value,
                    birth_date=file[6].value,
                    municipality_attention=Municipios.objects.get(codigo = file[7].value),
                    municipality_residence=Municipios.objects.get(codigo = file[8].value),
                )


class CargaMasivaHogaresAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_hogares]
admin.site.register(models.CargaMasivaHogares, CargaMasivaHogaresAdmin)