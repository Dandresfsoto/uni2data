from django.contrib import admin
from recursos_humanos import models
import openpyxl
from direccion_financiera.models import Proyecto
# Register your models here.


def actualizar_contratos(modeladmin, request, queryset):

    for data in queryset:
        wb = openpyxl.load_workbook(data.file)
        ws = wb.get_active_sheet()

        for file in ws.rows:

            if models.Contratistas.objects.filter(cedula = file[4].value).count() == 0:
                models.Contratistas.objects.create(
                    usuario_creacion = request.user,
                    usuario_actualizacion = request.user,
                    cedula = file[4].value,
                    nombres = file[2].value,
                    apellidos = file[3].value
                )

            if models.Contratos.objects.filter(nombre = file[0].value).count() == 0:
                models.Contratos.objects.create(
                    nombre = file[0].value,
                    contratista = models.Contratistas.objects.get(cedula = file[4].value),
                    inicio = file[7].value,
                    fin = file[8].value,
                    objeto_contrato = file[10].value,
                    tipo_contrato = file[11].value,
                    grupo_soportes = models.GruposSoportes.objects.get(id = file[12].value),
                    valor = file[9].value,
                    proyecto = Proyecto.objects.get(id = file[13].value),
                    cargo = models.Cargos.objects.get(id = file[14].value)
                )


class CargaMasivaContratosAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_contratos]
admin.site.register(models.CargaMasivaContratos, CargaMasivaContratosAdmin)

admin.site.register(models.Cargos)