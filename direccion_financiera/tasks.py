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
from desplazamiento.models import Solicitudes, Desplazamiento

@app.task
def build_reporte_interno(id, email):
    reporte = models.Reportes.objects.get(id=id)
    pagos = models.Pagos.objects.filter(reporte = reporte)


    if pagos.count() > 0:

        usuario = User.objects.get(email = email)
        cantidad = models.Pagos.objects.filter(reporte = reporte).count()

        output = BytesIO()
        wb = openpyxl.load_workbook(filename=settings.STATICFILES_DIRS[0] + '/documentos/reporte_'+ str(cantidad) +'.xlsx')
        ws = wb.get_sheet_by_name('REPORTE')
        logo_sican = Image(settings.STATICFILES_DIRS[0] + '/img/andes-logo.png')
        #logo_sican.drawing.top = 46
        #logo_sican.drawing.left = 66

        logo_sican.width = 200
        logo_sican.height = 170

        ws.add_image(logo_sican, 'C2')

        ws['F4'] = 'F-GAF-17-C' + str(reporte.consecutivo.id)
        ws['I4'] = reporte.reporte_update_datetime()
        ws['O4'] = usuario.get_full_name_string()

        if reporte.servicio.descontable:
            ws['F5'] = reporte.servicio.nombre + ' - DESCONTABLE'
        else:
            ws['F5'] = reporte.servicio.nombre
        ws['O5'] = reporte.proyecto.nombre


        if reporte.efectivo:
            ws['J6'] = 'PAGO EN EFECTIVO'
        else:
            ws['J6'] = 'CARGAR A LA CUENTA {0}'.format(reporte.proyecto.cuenta)

        ws['F6'] = reporte.tipo_soporte.nombre

        ws['F7'] = str(reporte.id)

        ws['G8'] = cantidad
        ws['K8'] = reporte.reporte_inicio_datetime()
        ws['O8'] = reporte.reporte_fin_datetime()

        i = 12

        for pago in pagos:
            ws['C'+str(i)] = 'ACTIVO'
            ws['D' + str(i)] = pago.tercero.cargo.nombre.upper()
            ws['E' + str(i)] = pago.tercero.fullname().upper()
            ws['G' + str(i)] = pago.tercero.cedula

            if reporte.efectivo:
                ws['H' + str(i)] = ''
                ws['I' + str(i)] = ''
                ws['J' + str(i)] = ''
            else:
                ws['H' + str(i)] = pago.tercero.banco.nombre.upper()
                ws['I' + str(i)] = pago.tercero.tipo_cuenta.upper()
                ws['J' + str(i)] = pago.tercero.cuenta
            ws['L' + str(i)] = pago.valor_descuentos().amount
            ws['O' + str(i)] = pago.observacion_pretty().upper()
            i += 1

        wb.save(output)

        filename = str(reporte.id) + '.xlsx'
        reporte.file.save(filename, File(output))

    return "Reporte generado"

@app.task
def send_mail_templated_pago(id,template,dictionary,from_email,list_to_email):
    try:
        send_mail(template, dictionary, from_email, list_to_email)
    except:
        pass
    else:
        models.Pagos.objects.filter(id = id).update(notificado = True)
    return 'Pago reportado a ' + str(list_to_email)

@app.task
def send_mail_templated_reporte(template,dictionary,from_email,list_to_email,attachments):
    send_mail(template, dictionary, from_email, list_to_email,attachments = attachments)
    return 'Email enviado'

@app.task
def build_listado_terceros(id):
    from recursos_humanos.models import Contratistas
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SICAN-LST-TERCEROS"


    titulos = ['Consecutivo', 'Nombres', 'Apellidos', 'Tipo identificación', '# Documento', 'Cargo', 'Usuario', 'Celular',
               'Correo', 'Fecha de nacimiento', '# Cuenta', 'Banco', 'Tipo de cuenta']

    formatos = ['0', 'General', 'General', 'General', '0', 'General', 'General', 'General',
                'General', 'dd/mm/yy', '0', 'General', 'General']

    ancho_columnas = [20, 30, 30, 25, 25, 35, 40, 20,
                      40, 25, 30, 30, 30]

    contenidos = []

    i = 0
    for tercero in Contratistas.objects.all().order_by('nombres'):
        i += 1
        contenidos.append([
            int(i),
            tercero.nombres,
            tercero.apellidos,
            tercero.get_tipo_identificacion(),
            tercero.cedula,
            tercero.get_cargo_nombre(),
            tercero.get_usuario_asociado(),
            str(tercero.celular),
            tercero.email,
            tercero.birthday,
            tercero.cuenta,
            tercero.get_banco(),
            tercero.tipo_cuenta
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    notificacion = Notifications.objects.create(
        user = reporte.usuario,
        title = 'Se ha construido un reporte',
        short_description = reporte.nombre,
        body = '<p style="display:inline;">Se ha construido el reporte <b>'+ reporte.nombre +
               '</b>, lo puedes decargar haciendo clic </p><a style="display:inline;" href="'+ reporte.url_file() +'">aqui</a>',
        icon = 'accessibility',
        color = 'orange-text text-darken-4'
    )

    return "Archivo paquete ID: " + filename

@app.task
def build_listado_tercero_especifico(id, tercero_id):

    reporte = models_reportes.Reportes.objects.get(id = id)

    proceso = "SICAN-PGS-TERCEROS"


    titulos = ['Consecutivo', 'Fecha', 'Usuario que reporta el pago', 'Consecutivo del reporte', 'Observación', 'Estado',
               'Valor inicial','Descuento 1','Descuento 2','Descuento 3',
               'Descuento 4','Descuento 5','Valor despues de descuentos']

    formatos = ['0', 'dd/mm/yy h:mm AM/PM', 'General', '0', 'General', 'General',
                '"$"#,##0_);("$"#,##0)', '"$"#,##0_);("$"#,##0)', '"$"#,##0_);("$"#,##0)', '"$"#,##0_);("$"#,##0)',
                '"$"#,##0_);("$"#,##0)','"$"#,##0_);("$"#,##0)','"$"#,##0_);("$"#,##0)','"$"#,##0_);("$"#,##0)']

    ancho_columnas = [20, 30, 30, 25, 30, 25,
                      20, 20, 20, 20,
                      20, 20, 30]

    contenidos = []

    pagos = models.Pagos.objects.filter(tercero__id = tercero_id).order_by('-creation')

    i = 0

    for pago in pagos:
        i += 1
        contenidos.append([
            int(i),
            pago.creation,
            pago.usuario_actualizacion.get_full_name_string(),
            pago.reporte.consecutivo.id,
            pago.observacion,
            pago.estado,
            pago.valor.amount.__float__()] + pago.get_list_descuentos() + [
            pago.valor_descuentos().__float__()
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    notificacion = Notifications.objects.create(
        user = reporte.usuario,
        title = 'Se ha completado un reporte',
        short_description = reporte.nombre,
        body = '<p style="display:inline;">Se ha construido el reporte <b>'+ reporte.nombre +
               '</b>, lo puedes decargar haciendo clic </p><a style="display:inline;" href="'+ reporte.url_file() +'">aqui</a>',
        icon = 'accessibility',
        color = 'orange-text text-darken-4'
    )

    return "Archivo paquete ID: " + filename

@app.task
def build_reporte_pagos(id):
    reporte = models_reportes.Reportes.objects.get(id = id)
    proceso = "SION-REPORTE-PAGOS"


    titulos = ['Consecutivo', 'Fecha creación', 'Reporte', 'Rubro presupuestal', 'Tipo','Nombre', 'Servicio', 'Proyecto', 'Contratista', 'Cedula', 'Valor inicial', 'Descuentos',
               'Valor','Estado', 'Tipo de cuenta', 'Banco', 'Cuenta', 'Cargo']

    formatos = ['0', 'dd/mm/yy', '0', 'General', 'General', 'General', 'General', 'General', 'General', '0', '"$"#,##0.00_);[Red]("$"#,##0.00)', '"$"#,##0.00_);[Red]("$"#,##0.00)',
                '"$"#,##0.00_);[Red]("$"#,##0.00)', 'General', 'General', 'General', 'General', 'General']

    ancho_columnas = [20, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30,30, 30,30, 30]

    contenidos = []

    i = 0
    for pago in models.Pagos.objects.all().order_by('creation'):
        i += 1
        contenidos.append([
            int(i),
            pago.creation,
            pago.reporte.consecutivo.id,
            pago.get_rubro(),
            'Efectivo' if pago.reporte.efectivo else 'Bancarizado',
            pago.reporte.nombre,
            pago.reporte.servicio.nombre,
            pago.reporte.proyecto.nombre,
            pago.tercero.get_full_name(),
            pago.tercero.cedula,
            pago.valor.amount,
            pago.valor_solo_descuentos_amount(),
            pago.valor_descuentos_amount(),
            pago.estado,
            pago.tipo_cuenta,
            pago.banco,
            pago.cuenta,
            pago.cargo
        ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Archivo paquete ID: " + filename


@app.task
def build_listado_solicitudes(id):

    reporte = models_reportes.Reportes.objects.get(id = id)

    proceso = "SICAN-SOLICITUDES-DESPLAZAMIENTO"


    titulos = ['Consecutivo','Contratista', 'Cedula', 'Consecutivo solicitud', 'Nombre',
               'Fecha', 'Origen', 'Destino', 'Tipo transporte', 'Transportador', 'Telefono',
               'Valor', 'Observaciones', 'Estado', 'Valor original']

    formatos = ['0', 'General', '0', '0', 'General',
                'dd/mm/yy', 'General', 'General', 'General', 'General', 'General',
                '"$"#,##0_);("$"#,##0)', 'General', 'General', '"$"#,##0_);("$"#,##0)']

    ancho_columnas = [20, 40, 40, 40, 40,
                      30, 30, 30, 30, 30 ,30,
                      30, 60, 30, 30]

    contenidos = []


    i = 0

    for solicitud in Solicitudes.objects.all().order_by('creation'):
        for desplazamiento in Desplazamiento.objects.filter(solicitud = solicitud).order_by('creation'):
            i += 1
            contenidos.append([
                int(i),
                solicitud.get_contratista(),
                solicitud.get_contratista_cedula(),
                solicitud.consecutivo,
                solicitud.nombre,
                desplazamiento.fecha,
                desplazamiento.origen,
                desplazamiento.destino,
                desplazamiento.tipo_transporte,
                desplazamiento.transportador,
                desplazamiento.telefono,
                desplazamiento.valor.amount.__float__(),
                desplazamiento.observaciones,
                desplazamiento.verificado,
                desplazamiento.valor_original.amount.__float__()
            ])

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    notificacion = Notifications.objects.create(
        user = reporte.usuario,
        title = 'Se ha completado un reporte',
        short_description = reporte.nombre,
        body = '<p style="display:inline;">Se ha construido el reporte <b>'+ reporte.nombre +
               '</b>, lo puedes decargar haciendo clic </p><a style="display:inline;" href="'+ reporte.url_file() +'">aqui</a>',
        icon = 'accessibility',
        color = 'orange-text text-darken-4'
    )

    return "Archivo paquete ID: " + filename