from django.contrib import admin
from cpe_2018 import models
import json
from django.db.models import Sum
# Register your models here.

admin.site.register(models.Componentes)
admin.site.register(models.Estrategias)
admin.site.register(models.Momentos)
admin.site.register(models.Entregables)
admin.site.register(models.Departamentos)
admin.site.register(models.Municipios)
admin.site.register(models.ActualizacionProductosFinales)


def actualizar_actividades(modeladmin, request, queryset):

    for grupo in queryset:
        for docente in models.Docentes.objects.filter(grupo = grupo):
            docente.actualizar_objetos_formacion_estrategia(grupo.ruta, grupo)


class GruposAdmin(admin.ModelAdmin):
    list_display = ['get_nombre_grupo']
    actions = [actualizar_actividades]
admin.site.register(models.Grupos, GruposAdmin)




def construir_red(modeladmin, request, queryset):

    for red in queryset:
        red.generar_red()


class RedAdmin(admin.ModelAdmin):
    list_display = ['consecutivo']
    actions = [construir_red]
admin.site.register(models.Red, RedAdmin)



def actualizar_valores_acceso_ruta(modeladmin, request, queryset):

    for ruta in queryset:
        ruta.actualizar_valores_acceso()


class RutasAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    actions = [actualizar_valores_acceso_ruta]

admin.site.register(models.Rutas,RutasAdmin)


admin.site.register(models.EntregableRutaObject)


def generar_excel_corte(modeladmin, request, queryset):

    for corte in queryset:
        corte.create_excel()


class CortesAdmin(admin.ModelAdmin):
    list_display = ['consecutivo']
    actions = [generar_excel_corte]

admin.site.register(models.Cortes,CortesAdmin)



def calcular_actualizacion(modeladmin, request, queryset):

    for actualizacion in queryset:
        actualizacion.construir()


class ActualizacionLupaapAdmin(admin.ModelAdmin):
    list_display = ['fecha']
    actions = [calcular_actualizacion]

admin.site.register(models.ActualizacionLupaap,ActualizacionLupaapAdmin)





def calcular_actualizacion_autoreporte_evaluacion(modeladmin, request, queryset):

    for actualizacion in queryset:
        actualizacion.construir()


class ActualizacionAutoreporteEvaluacionAdmin(admin.ModelAdmin):
    list_display = ['fecha']
    actions = [calcular_actualizacion_autoreporte_evaluacion]

admin.site.register(models.ActualizacionAutoreporteEvaluacion,ActualizacionAutoreporteEvaluacionAdmin)