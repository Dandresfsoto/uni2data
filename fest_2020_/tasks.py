from __future__ import absolute_import, unicode_literals
from config.celery import app
import openpyxl
from io import BytesIO
from usuarios.models import User
from django.conf import settings
from openpyxl.drawing.image import Image
from django.core.files import File
from mail_templated import send_mail
from direccion_financiera import models
from config.functions import construir_reporte, construir_reporte_pagina
from reportes import models as models_reportes
from usuarios.models import Notifications
from fest_2020_ import models
from fest_2020_.modelos_instrumentos import get_modelo
from six.moves.urllib import parse as urlparse
import os
import ftplib
import io
import datetime
import json
import shutil
from django.utils import timezone
from io import BytesIO


@app.task
def send_mail_templated_liquidacion(template,dictionary,from_email,list_to_email):
    send_mail(template, dictionary, from_email, list_to_email)
    return 'Email enviado'

@app.task
def send_mail_templated_cuenta_cobro(template,dictionary,from_email,list_to_email):
    send_mail(template, dictionary, from_email, list_to_email)
    return 'Email enviado'

@app.task
def build_informe_instrumento(id, instrumento_id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    instrumento = models.Instrumentos.objects.get(id = instrumento_id)
    modelo = get_modelo(instrumento.modelo)['model']
    proceso = "SICAN-FEST 2020"
    order = []
    titulos = []
    formatos = []
    ancho_columnas = []
    contenidos = []

    for field in modelo._meta.get_fields():
        order.append(field.name)
        titulos.append(field.name)
        formatos.append('General')
        ancho_columnas.append(30)

    for data in modelo.objects.filter(instrumento = instrumento):
        lista = []
        for name in order:
            obj = getattr(data, name)

            if name == 'hogares':
                value = ''
                for hogar in obj.all():
                    value += str(hogar.documento) + ', '

                lista.append(value[:-2])
            else:
                lista.append(str(obj))
        contenidos.append(lista)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)


    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte generado: " + filename

@app.task
def build_tablero_control_componente(id, id_componente):
    reporte = models_reportes.Reportes.objects.get(id=id)
    componente = models.Componentes.objects.get(id=id_componente)
    proceso = "IRACA 2021"

    titulos = ['Consecutivo', 'Cedula', 'Nombre']
    formatos = ['0', 'General', 'General']
    ancho_columnas = [20, 30, 50]
    contenidos = []
    order = []


    for momento in models.Momentos.objects.filter(componente=componente).order_by('consecutivo'):
        order.append(momento)
        titulos.append(f'{momento.nombre}')
        titulos.append(f'Gestor')
        titulos.append(f'Ruta')
        formatos.append('General')
        formatos.append('General')
        formatos.append('General')
        ancho_columnas.append(30)
        ancho_columnas.append(30)
        ancho_columnas.append(30)

    i = 0

    hogares = models.Hogares.objects.filter(rutas__componente=componente).distinct()
    for hogar in hogares:
        rutas = hogar.rutas.all()
        for ruta in rutas:

            i += 1

            lista = [
                i,
                str(hogar.documento),
                str(hogar.get_full_name())
            ]

            for momento in order:

                lista.append(hogar.get_estado_momento(momento, ruta))
                lista.append(ruta.contrato.contratista.cedula)
                lista.append(ruta.nombre)

            contenidos.append(lista)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename


@app.task
def build_reporte_acumulado(id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SICAN-REPORTE-CORTES"


    titulos = ['Consecutivo','Cedula','Nombre del contratista','Valor','Estado','Numero de Consecutivo del Corte','Fecha de creacion del Corte','Descripcion del Corte' ]

    formatos = ['0','0','General','0','General','General','General','General','General']

    ancho_columnas = [20, 30, 30, 30, 30, 30, 30, 30]

    contenidos = []
    order = []

    i = 0
    for cuenta in models.CuentasCobro.objects.all().order_by('creation'):
        i += 1
        contenidos.append([
            int(i),
            cuenta.ruta.contrato.contratista.get_cedula(),
            cuenta.ruta.contrato.contratista.get_full_name(),
            cuenta.get_valor(),
            cuenta.estado,
            cuenta.get_consecutivo_corte(),
            cuenta.get_fecha_corte(),
            cuenta.get_descripcion_corte(),
        ])



    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Archivo paquete ID: " + filename

