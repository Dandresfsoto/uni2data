from __future__ import absolute_import, unicode_literals
from config.celery import app
from config.functions import construir_reporte
from usuarios.models import PaqueteActivacion, CodigoActivacion, User
from django.core.files import File
from usuarios.models import Notifications
from mail_templated import send_mail
from django.conf import settings
from direccion_financiera.models import Reportes
from django.utils import timezone
import os


@app.task
def build_file_paquete_activacion(id, email):

    nombre = "Paquete de activación"
    proceso = "SICAN-USRPAQ"
    paquete = PaqueteActivacion.objects.get(id=id)
    fecha = paquete.creation
    usuario = User.objects.get(email=email)


    for i in range(0, paquete.generados):
        codigo = CodigoActivacion.objects.create(paquete = paquete)
        codigo.permissions.set(paquete.permissions.all())
        codigo.save()


    titulos = ['Consecutivo','Código']

    formatos = ['0', 'General']

    ancho_columnas = [20,40]

    contenidos = []

    i = 0
    for codigo in CodigoActivacion.objects.filter(paquete = paquete):
        i += 1
        contenidos.append([
            int(i),
            str(codigo.id)
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, nombre, fecha, usuario, proceso)

    filename = str(paquete.id) + '.xlsx'
    paquete.file.save(filename, File(output))

    notificacion = Notifications.objects.create(
        user = usuario,
        title = 'Nuevo paquete de códigos',
        short_description = 'Se ha creado el paquete de códigos ' + paquete.description,
        body = '<p style="display:inline;">Se ha creado el paquete de códigos <b>'+ paquete.description +
               '</b> lo puedes decargar haciendo clic </p><a style="display:inline;" href="'+ paquete.file.url +'">aqui</a>',
        icon = 'code',
        color = 'blue-text text-darken-2'
    )

    return "Archivo paquete ID: " + filename

@app.task
def send_mail_templated(template,dictionary,from_email,list_to_email):
    send_mail(template, dictionary, from_email, list_to_email)
    return 'Email enviado a ' + str(list_to_email)

@app.task
def add(x, y):
    return x + y

@app.task
def reportes_pendientes():

    url_base = 'https://sican.asoandes.org'

    reportados = Reportes.objects.filter(estado = 'Reportado').order_by('-consecutivo__id')
    en_pagaduria = Reportes.objects.filter(estado='En pagaduria').order_by('-consecutivo__id')

    reportados_text = ''
    en_pagaduria_text = ''

    i = 1
    for reportado in reportados:
        if i == 1:
            reportados_text += '<p style="margin-top: 40px;"><b>Reporte : ' + str(
                reportado.consecutivo.id) + '  </b>' + reportado.nombre + ' - ' + reportado.pretty_print_valor_descuentos() + '</p>'
        else:
            reportados_text += '<p><b>Reporte : ' + str(
                reportado.consecutivo.id) + '  </b>' + reportado.nombre + ' - ' + reportado.pretty_print_valor_descuentos() + '</p>'
        i += 1


    i = 1
    for reportado in en_pagaduria:
        if i == 1:
            en_pagaduria_text += '<p style="margin-top: 40px;"><b>Reporte : ' + str(
                reportado.consecutivo.id) + '  </b>' + reportado.nombre + ' - ' + reportado.pretty_print_valor_descuentos() + '</p>'
        else:
            en_pagaduria_text += '<p><b>Reporte : ' + str(
                reportado.consecutivo.id) + '  </b>' + reportado.nombre + ' - ' + reportado.pretty_print_valor_descuentos() + '</p>'
        i += 1

    send_mail(
        'mail/direccion_financiera/recordatorio_pendientes/reportes.tpl',
        {
            'url_base': url_base,
            'reportados': reportados_text,
            'pagaduria': en_pagaduria_text
        },
        settings.DEFAULT_FROM_EMAIL,
        [
            settings.EMAIL_DIRECCION_FINANCIERA,
            settings.EMAIL_GERENCIA,
            settings.EMAIL_HOST_USER
        ]
    )
    return "Recordatorio reportes"

@app.task
def respaldo_db():
    time = timezone.now()
    filename = '{0}.sql'.format(time.strftime("%Y_%m_%d_%H_%M_%S"))
    os.system('pg_dump -U {0} {1} > C:\\DB_SICAN\\{2}'.format(os.getenv('POSTGRES_USER'),os.getenv('POSTGRES_DB'),filename))
    return "Respaldo realizado"