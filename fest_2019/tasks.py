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
from fest_2019 import models
from fest_2019.modelos_instrumentos import get_modelo
from six.moves.urllib import parse as urlparse
import os
import ftplib
import io
import datetime
import json
import shutil
from django.utils import timezone

@app.task
def send_mail_templated_cuenta_cobro(template,dictionary,from_email,list_to_email):
    send_mail(template, dictionary, from_email, list_to_email)
    return 'Email enviado'

@app.task
def build_informe_instrumento(id, instrumento_id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SICAN-FEST 2019"
    instrumento = models.Instrumentos.objects.get(id = instrumento_id)
    modelo = get_modelo(instrumento.modelo)['model']
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

            if name == 'hogar':
                lista.append(obj.documento)
            else:
                lista.append(str(obj))
        contenidos.append(lista)




    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)


    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte generado: " + filename

@app.task
def build_ruteo(id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SICAN-RUTEO"

    titulos = ['Consecutivo', 'Cedula', 'Nombre', 'Ruta vinculación', 'Documento contratista', 'Nombre contratista','Valor reportado']

    formatos = ['0', '0', 'General', 'General', '0', 'General','"$"#,##0_);("$"#,##0)']

    ancho_columnas = [20, 30, 50, 50, 50, 50, 50]

    contenidos = []

    i = 0
    for hogar in models.Hogares.objects.all():

        i += 1

        ruta = hogar.get_ruta_vinculacion()

        contenidos.append([
            int(i),
            hogar.documento,
            hogar.get_full_name(),
            hogar.get_nombre_ruta_vinculacion(),
            '' if ruta == None else ruta.contrato.contratista.cedula,
            '' if ruta == None else ruta.contrato.contratista.get_full_name(),
            hogar.get_valor_ruta_vinculacion()
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)



    titulos = ['Consecutivo', 'Cedula', 'Nombre', 'Ruta Componente Fortalecimiento social y comunitario','Documento contratista', 'Nombre contratista']

    formatos = ['0', '0', 'General', 'General', '0', 'General']

    ancho_columnas = [20, 30, 50, 50, 50, 50]

    contenidos = []

    componente = models.Componentes.objects.get(consecutivo = 1)



    for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente = componente).order_by('nombre'):
        titulos.append(momento.nombre)
        formatos.append('"$"#,##0_);("$"#,##0)')
        ancho_columnas.append(30)


    i = 0
    for hogar in models.Hogares.objects.all():
        i += 1

        ruta = hogar.get_ruta_componente(componente)

        valores = []

        for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente=componente).order_by('nombre'):
            valores.append(momento.get_valor_pagado(hogar))


        contenidos.append([
            int(i),
            hogar.documento,
            hogar.get_full_name(),
            hogar.get_nombre_ruta_componente(componente),
            '' if ruta == None else ruta.contrato.contratista.cedula,
            '' if ruta == None else ruta.contrato.contratista.get_full_name(),
        ]+valores)



    output2 = construir_reporte_pagina(output,'Hoja2',titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    titulos = ['Consecutivo', 'Cedula', 'Nombre', 'Ruta Componente Seguridad alimentaria','Documento contratista', 'Nombre contratista']

    formatos = ['0', '0', 'General', 'General', '0', 'General']

    ancho_columnas = [20, 30, 50, 50, 50, 50]

    contenidos = []

    componente = models.Componentes.objects.get(consecutivo=2)

    for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente = componente).order_by('nombre'):
        titulos.append(momento.nombre)
        formatos.append('"$"#,##0_);("$"#,##0)')
        ancho_columnas.append(30)

    i = 0
    for hogar in models.Hogares.objects.all():
        i += 1

        ruta = hogar.get_ruta_componente(componente)

        valores = []

        for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente=componente).order_by(
                'nombre'):
            valores.append(momento.get_valor_pagado(hogar))

        contenidos.append([
                              int(i),
                              hogar.documento,
                              hogar.get_full_name(),
                              hogar.get_nombre_ruta_componente(componente),
                              '' if ruta == None else ruta.contrato.contratista.cedula,
                              '' if ruta == None else ruta.contrato.contratista.get_full_name(),
                          ] + valores)

    output3 = construir_reporte_pagina(output2, 'Hoja3', titulos, contenidos, formatos, ancho_columnas, reporte.nombre,
                                       reporte.creation, reporte.usuario, proceso)

    titulos = ['Consecutivo', 'Cedula', 'Nombre', 'Ruta Componente Vivir mi casa','Documento contratista', 'Nombre contratista']

    formatos = ['0', '0', 'General', 'General', '0', 'General']

    ancho_columnas = [20, 30, 50, 50, 50, 50]

    contenidos = []

    componente = models.Componentes.objects.get(consecutivo=3)

    for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente = componente).order_by('nombre'):
        titulos.append(momento.nombre)
        formatos.append('"$"#,##0_);("$"#,##0)')
        ancho_columnas.append(30)

    i = 0
    for hogar in models.Hogares.objects.all():
        i += 1

        ruta = hogar.get_ruta_componente(componente)

        valores = []

        for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente=componente).order_by('nombre'):
            valores.append(momento.get_valor_pagado(hogar))

        contenidos.append([
                              int(i),
                              hogar.documento,
                              hogar.get_full_name(),
                              hogar.get_nombre_ruta_componente(componente),
                              '' if ruta == None else ruta.contrato.contratista.cedula,
                              '' if ruta == None else ruta.contrato.contratista.get_full_name(),
                          ] + valores)

    output4 = construir_reporte_pagina(output3, 'Hoja4', titulos, contenidos, formatos, ancho_columnas, reporte.nombre,
                                       reporte.creation, reporte.usuario, proceso)

    titulos = ['Consecutivo', 'Cedula', 'Nombre', 'Ruta Componente Proyecto productivo','Documento contratista', 'Nombre contratista']

    formatos = ['0', '0', 'General', 'General', '0', 'General']

    ancho_columnas = [20, 30, 50, 50, 50, 50]

    contenidos = []

    componente = models.Componentes.objects.get(consecutivo=4)

    for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente = componente).order_by('nombre'):
        titulos.append(momento.nombre)
        formatos.append('"$"#,##0_);("$"#,##0)')
        ancho_columnas.append(30)

    i = 0
    for hogar in models.Hogares.objects.all():
        i += 1

        ruta = hogar.get_ruta_componente(componente)

        valores = []

        for momento in models.Momentos.objects.exclude(tipo='vinculacion').filter(componente=componente).order_by('nombre'):
            valores.append(momento.get_valor_pagado(hogar))

        contenidos.append([
                              int(i),
                              hogar.documento,
                              hogar.get_full_name(),
                              hogar.get_nombre_ruta_componente(componente),
                              '' if ruta == None else ruta.contrato.contratista.cedula,
                              '' if ruta == None else ruta.contrato.contratista.get_full_name(),
                          ] + valores)

    output5 = construir_reporte_pagina(output4, 'Hoja5', titulos, contenidos, formatos, ancho_columnas, reporte.nombre,
                                       reporte.creation, reporte.usuario, proceso)




    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output5))


    return "Ruteo generado: " + filename

@app.task
def build_informe_actividades(id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "IRACA"

    titulos = ['Consecutivo', 'Ruta', 'Contratista', 'Cedula','Actividad', 'Hogares', 'Departamentos','Estado', 'Valor']

    formatos = ['0', 'General', 'General', '0', 'General', 'General', 'General', 'General', '"$"#,##0_);("$"#,##0)']

    ancho_columnas = [20, 30, 50, 50, 50, 50, 50, 50, 50]

    contenidos = []

    i = 0

    for ins in models.InstrumentosRutaObject.objects.all():
        i += 1
        contenidos.append([
            int(i),
            ins.ruta.nombre,
            ins.ruta.contrato.contratista.get_full_name(),
            ins.ruta.contrato.contratista.cedula,
            ins.instrumento.nombre,
            ins.get_hogares_reporte(),
            ins.get_departamentos_reporte(),
            ins.estado,
            '' if ins.cupo_object == None else ins.cupo_object.valor.amount
        ])


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)


    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte generado: " + filename

@app.task
def build_informe_georeferenciacion(id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "IRACA"

    titulos = ["Consecutivo" ,"Tipo", "Nombre / Codigo", "Fecha creación", "Latitud", "Longitud", "Altitud", "Precisión", "Resguardo", "Comunidad", "Validez", "Gestor", "Documento"]

    formatos = ['General','General', 'General', 'dd/mm/yyyy', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General']

    ancho_columnas = [20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50]

    contenidos = []

    i = 0

    for item in models.GeoreferenciacionApi.objects.all():
        i += 1
        contenidos.append([
            int(i),
            'Proyecto' if 'type' in item.json['data'].keys() else 'Hogar',
            item.json['data']['code'] if 'type' in item.json['data'].keys() else f'{item.json["data"]["name"]} - {item.json["data"]["document"]}',
            timezone.localtime(item.creation),
            item.json['data']['position']['coords']['latitude'],
            item.json['data']['position']['coords']['longitude'],
            int(item.json['data']['position']['coords']['altitude']),
            int(item.json['data']['position']['coords']['accuracy']),
            f"{item.json['data']['guard']}" if 'guard' in item.json['data'].keys() else "",
            f"{item.json['data']['community']}" if 'community' in item.json['data'].keys() else "",
            "Valido" if not item.json['data']['position']['mocked'] else "Invalido",
            item.json['nombre'],
            item.json['documento'],
        ])


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)


    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte generado: " + filename
