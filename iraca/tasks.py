from __future__ import absolute_import, unicode_literals
from config.celery import app
from config.functions import construir_reporte, construir_reporte_pagina
from mail_templated import send_mail
from django.core.files import File

from iraca.models import Moments, Households, Instruments
from iraca.models_instruments import get_model
from reportes import models as models_reportes



@app.task
def build_control_panel_Implementation(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['Consecutivo', 'Cedula', 'Nombre']
    formatos = ['0', 'General', 'General']
    ancho_columnas = [20, 30, 50]
    contenidos = []
    order = []


    for moment in Moments.objects.filter(type_moment="implementacion").order_by('consecutive'):
        order.append(moment)
        titulos.append(f'{moment.name}')
        titulos.append(f'Ruta')
        formatos.append('General')
        formatos.append('General')
        ancho_columnas.append(30)
        ancho_columnas.append(30)

    i = 0

    households = Households.objects.filter().distinct()
    for household in households:
        routes = household.routes.all()
        for route in routes:

            i += 1

            list = [
                i,
                str(household.document),
                str(household.get_full_name())
            ]

            for moment in order:

                list.append(household.get_estate_moment(moment, route))
                list.append(route.name)

            contenidos.append(list)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename

@app.task
def build_control_panel_Formulation(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['Consecutivo', 'Cedula', 'Nombre']
    formatos = ['0', 'General', 'General']
    ancho_columnas = [20, 30, 50]
    contenidos = []
    order = []


    for moment in Moments.objects.filter(type_moment="formulacion").order_by('consecutive'):
        order.append(moment)
        titulos.append(f'{moment.name}')
        titulos.append(f'Ruta')
        formatos.append('General')
        formatos.append('General')
        ancho_columnas.append(30)
        ancho_columnas.append(30)

    i = 0

    households = Households.objects.filter().distinct()
    for household in households:
        routes = household.routes.all()
        for route in routes:

            i += 1

            list = [
                i,
                str(household.document),
                str(household.get_full_name())
            ]

            for moment in order:

                list.append(household.get_estate_moment(moment, route))
                list.append(route.name)

            contenidos.append(list)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename

@app.task
def build_report_instrument(id, instrument_id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    instrument = Instruments.objects.get(id = instrument_id)
    model = get_model(instrument.model)['model']
    proceso = "SICAN-IRACA 2021"
    order = []
    titulos = []
    formatos = []
    ancho_columnas = []
    contenidos = []

    for field in model._meta.get_fields():
        order.append(field.name)
        titulos.append(field.verbose_name)
        formatos.append('General')
        ancho_columnas.append(30)

    for data in model.objects.filter(instrument = instrument):
        lista = []
        for name in order:
            obj = getattr(data, name)

            if name == 'households':
                value = ''
                for household in obj.all():
                    value += str(household.document) + ', '

                lista.append(value[:-2])
            else:
                lista.append(str(obj))
        contenidos.append(lista)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)


    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte generado: " + filename