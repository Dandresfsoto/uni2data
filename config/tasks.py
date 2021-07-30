from __future__ import absolute_import, unicode_literals
from config.celery import app
from mail_templated import send_mail
from django.conf import settings
from direccion_financiera.models import Reportes
from django.utils import timezone
import os

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