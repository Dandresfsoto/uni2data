from __future__ import absolute_import, unicode_literals
from config.celery import app
from mail_templated import send_mail
import openpyxl
from django.conf import settings
from io import BytesIO
from recursos_humanos import models
from django.core.files import File
from reportes import models as models_reportes
from config.functions import construir_reporte
from entes_territoriales import models


@app.task
def build_estado_hitos(id):

    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SICAN-ESTADO-HITOS"


    titulos = ['Consecutivo', 'Encargado', 'Municipio', 'Departamento','Región', 'Tipo' ,'Clase','Fecha', 'Estado', 'Observación']

    formatos = ['0', 'General', 'General', 'General','General', 'General', 'General', 'dd/mm/yyyy', 'General', 'General']

    ancho_columnas = [20, 30, 30, 30, 30, 30, 30, 40, 25, 50]

    contenidos = []


    i = 0
    for hito in models.Hito.objects.all().order_by('-creation'):
        i += 1

        contenidos.append([
            int(i),
            hito.reunion.usuario_creacion.get_full_name_string(),
            hito.reunion.municipio.nombre,
            hito.reunion.municipio.departamento.nombre,
            hito.reunion.get_region(),
            hito.tipo,
            hito.clase,
            hito.fecha,
            hito.estado,
            hito.observacion
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Archivo paquete ID: " + filename