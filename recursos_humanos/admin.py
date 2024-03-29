from django.contrib import admin
from recursos_humanos import models
import openpyxl
from direccion_financiera.models import Proyecto
# Register your models here.


def actualizar_contratos(modeladmin, request, queryset):

    for data in queryset:
        wb = openpyxl.load_workbook(data.file)
        ws = wb.active

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
                    transporte = file[15].value,
                    proyecto = Proyecto.objects.get(id = file[13].value),
                    cargo = models.Cargos.objects.get(id = file[14].value),
                    suscrito=True,
                    ejecucion=True,
                )
            if models.Contratos.objects.filter(nombre = file[0].value).count() != 0:
                contrato = models.Contratos.objects.get(nombre = file[0].value)
                contrato.valor_mensual = file[16].value
                contrato.save()

def actualizar_otros_si(modeladmin, request, queryset):

    for data in queryset:
        wb = openpyxl.load_workbook(data.file)
        ws = wb.active

        for file in ws.rows:

            if models.Contratos.objects.filter(nombre = file[0].value).count() != 0:
                contrato = models.Contratos.objects.get(nombre = file[0].value)
                otro_si = models.Otros_si.objects.create(
                    nombre = file[2].value,
                    contrato = contrato,
                    inicio = file[3].value,
                    fin = file[4].value,
                    fecha_original = contrato.fin,
                    valor=file[5].value,
                    valor_total=file[6].value,
                )
                otro_si.save()
                contrato.fin=file[4].value
                contrato.valor=otro_si.valor+contrato.valor
                contrato.save()

class CargaMasivaContratosAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_contratos]
admin.site.register(models.CargaMasivaContratos, CargaMasivaContratosAdmin)

class CargaMasivaOtrosiAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_otros_si]
admin.site.register(models.CargaMasivaOtrosSi, CargaMasivaOtrosiAdmin)

admin.site.register(models.Cargos)
admin.site.register(models.CargosHv)
admin.site.register(models.Contratistas)
admin.site.register(models.Cuts)
admin.site.register(models.Collects_Account)
admin.site.register(models.Contratos)
admin.site.register(models.Registration)
admin.site.register(models.Liquidations)
admin.site.register(models.Certificaciones)
admin.site.register(models.GruposSoportes)
admin.site.register(models.Otros_si)