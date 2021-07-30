from django.contrib import admin
from direccion_financiera import models

# Register your models here.

admin.site.register(models.Servicios)
admin.site.register(models.TipoSoporte)
admin.site.register(models.Proyecto)
admin.site.register(models.Descuentos)
admin.site.register(models.RubroPresupuestal)

def delete_reporte(modeladmin, request, queryset):
    for reporte in queryset:
        pagos = models.Pagos.objects.filter(reporte = reporte)
        descuentos = models.Descuentos.objects.filter(pago__id__in = pagos.values_list('id',flat=True)).delete()
        amortizaciones = models.Amortizaciones.objects.filter(pago__id__in = pagos.values_list('id',flat=True)).delete()
        pagos.delete()
        reporte.delete()

delete_reporte.short_description = "Borrar reporte"

class ReportesAdmin(admin.ModelAdmin):
    list_display = ['consecutivo']
    ordering = ['consecutivo']
    actions = [delete_reporte]

admin.site.register(models.Reportes, ReportesAdmin)
admin.site.register(models.Pagos)
admin.site.register(models.Bancos)