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
from config.functions import construir_reporte
from reportes import models as models_reportes
from usuarios.models import Notifications
from six.moves.urllib import parse as urlparse
import os
import ftplib
import io
from reportes.models import Reportes
from ofertas import models
from usuarios import models as user_models

@app.task
def build_estado_aplicacion_oferta(id, oferta_id):

    oferta = models.Ofertas.objects.get(id = oferta_id)
    reporte = Reportes.objects.get(id=id)


    titulos = [
        'Consecutivo', 'Fecha de aplicación', 'Nombres', 'Apellidos', 'Cedúla','Email','Dirección','Celular','Sexo','Tipo de sangre',
        'Fecha de nacimiento','Lugar de nacimiento', 'Lugar de expedición de la cedúla', 'Lugar de residencia',
        'Municipios de aplicación','Perfil', 'Experiencia', 'Selección', 'Observación', 'Nivel académico'
    ]

    formatos = ['0', 'dd/mm/yyyy hh:mm:ss AM/PM', 'General', 'General', '0', 'General', 'General', 'General', 'General', 'General',
                'dd/mm/yyyy', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General']

    ancho_columnas = [20, 40, 40, 40, 40, 40, 40, 40, 40, 40,
                      40, 40, 40, 40,
                      40, 40, 40, 40, 40, 40]

    contenidos = []

    i = 1



    for aplicacion in models.AplicacionOferta.objects.filter(oferta = oferta).order_by('creation'):


        contenidos.append([
            i,
            aplicacion.creation,
            aplicacion.usuario.first_name.upper(),
            aplicacion.usuario.last_name.upper(),
            aplicacion.usuario.cedula,
            aplicacion.usuario.email,
            aplicacion.usuario.direccion.upper(),
            str(aplicacion.usuario.celular),
            aplicacion.usuario.sexo.upper(),
            aplicacion.usuario.tipo_sangre,
            aplicacion.usuario.birthday,
            str(aplicacion.usuario.lugar_nacimiento).upper(),
            str(aplicacion.usuario.lugar_expedicion).upper(),
            str(aplicacion.usuario.lugar_residencia).upper(),
            aplicacion.get_municipios_string(),
            aplicacion.cualificacion_perfil,
            aplicacion.cualificacion_experiencia,
            aplicacion.cualificacion_seleccion,
            aplicacion.cualificacion_observacion,
            aplicacion.usuario.get_nivel_academico()
        ])

        i += 1

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, 'OFERTAS LABORALES')

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Reporte completo"