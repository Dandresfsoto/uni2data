from django.db.models import Sum

from config.celery import app
import openpyxl
from io import BytesIO
from django.conf import settings
from openpyxl.drawing.image import Image
from django.core.files import File

from inventario.models import Despachos, Sustracciones
from reportes.models import Reportes


@app.task
def build_remision(id):
    despacho = Despachos.objects.get(id=id)
    sustracciones = Sustracciones.objects.filter(despacho = despacho)


    if sustracciones.count() > 0 and sustracciones.count() <= 19:

        cantidad = Sustracciones.objects.filter(despacho = despacho).count()

        output = BytesIO()
        wb = openpyxl.load_workbook(filename=settings.STATICFILES_DIRS[0] + '/documentos/despacho_1.xlsx')
        ws = wb.get_sheet_by_name('remision')
        #logo_sican.drawing.top = 46
        #logo_sican.drawing.left = 66

        ws.merge_cells('G3:J5')
        top_left_cell = ws['G3']
        top_left_cell.value = str(despacho.consecutivo)

        ws['B6'] = str(despacho.nombre_cliente)
        ws['D6'] = str(despacho.ciudad.nombre)
        ws['H6'] = str(despacho.pretty_fecha_envio_datetime())

        ws['B7'] = str(despacho.documento)
        ws['D7'] = str(despacho.direccion)
        ws['D7'] = str(despacho.direccion)

        if despacho.transportador != None and despacho.transportador != "":
            ws['B8'] = str(despacho.transportador)
        if despacho.conductor != None and despacho.conductor != "":
            ws['E8'] = str(despacho.conductor)
        if despacho.placa != None and despacho.placa != "":
            ws['J8'] = str(despacho.placa)

        i = 12
        contador = 1

        for sustraccion in sustracciones:


            ws['A' + str(i)] = contador
            ws['B' + str(i)] = sustraccion.producto.nombre
            ws['G' + str(i)] = sustraccion.cantidad
            ws['H' + str(i)] = str(str(sustraccion.producto.valor).replace('COL',''))
            ws['I' + str(i)] = str(str(sustraccion.producto.impuesto) + "%")
            ws['J' + str(i)] = str(sustraccion.pretty_print_valor_total())

            i += 1
            contador += 1

        total = sustracciones.aggregate(Sum('valor_total'))['valor_total__sum']
        total = "${:,.2f}".format(total)
        ws['J33'] = total

        ws['A31'] = despacho.observacion

        wb.save(output)

        filename = str(despacho.id) + '.xlsx'
        despacho.respaldo.save(filename, File(output))

    elif sustracciones.count() > 19 and sustracciones.count() <= 41:

        cantidad = Sustracciones.objects.filter(despacho = despacho).count()

        output = BytesIO()
        wb = openpyxl.load_workbook(filename=settings.STATICFILES_DIRS[0] + '/documentos/despacho_2.xlsx')
        ws = wb.get_sheet_by_name('remision')
        #logo_sican.drawing.top = 46
        #logo_sican.drawing.left = 66

        ws.merge_cells('G3:J5')
        top_left_cell = ws['G3']
        top_left_cell.value = str(despacho.consecutivo)

        ws.merge_cells('G40:J42')
        top_left_cell = ws['G40']
        top_left_cell.value = str(despacho.consecutivo)

        ws['B6'] = str(despacho.nombre_cliente)
        ws['D6'] = str(despacho.ciudad.nombre)
        ws['H6'] = str(despacho.pretty_fecha_envio_datetime())

        ws['B7'] = str(despacho.documento)
        ws['D7'] = str(despacho.direccion)
        ws['D7'] = str(despacho.direccion)

        if despacho.transportador != None and despacho.transportador != "":
            ws['B8'] = str(despacho.transportador)
        if despacho.conductor != None and despacho.conductor != "":
            ws['E8'] = str(despacho.conductor)
        if despacho.placa != None and despacho.placa != "":
            ws['J8'] = str(despacho.placa)

        i = 12
        contador = 1

        for sustraccion in sustracciones:


            ws['A' + str(i)] = contador
            ws['B' + str(i)] = sustraccion.producto.nombre
            ws['G' + str(i)] = sustraccion.cantidad
            ws['H' + str(i)] = str(str(sustraccion.producto.valor).replace('COL',''))
            ws['I' + str(i)] = str(str(sustraccion.producto.impuesto) + "%")
            ws['J' + str(i)] = str(sustraccion.pretty_print_valor_total())

            i += 1
            contador += 1
            if contador == 20:
                i = i + 16

        total = sustracciones.aggregate(Sum('valor_total'))['valor_total__sum']
        total = "${:,.2f}".format(total)
        ws['J70'] = total

        ws['A68'] = despacho.observacion

        wb.save(output)

        filename = str(despacho.id) + '.xlsx'
        despacho.respaldo.save(filename, File(output))

    elif sustracciones.count() > 42 and sustracciones.count() <= 63:

        output = BytesIO()
        wb = openpyxl.load_workbook(filename=settings.STATICFILES_DIRS[0] + '/documentos/despacho_2.xlsx')
        ws = wb.get_sheet_by_name('remision')
        #logo_sican.drawing.top = 46
        #logo_sican.drawing.left = 66

        ws.merge_cells('G3:J5')
        top_left_cell = ws['G3']
        top_left_cell.value = str(despacho.consecutivo)

        ws.merge_cells('G40:J42')
        top_left_cell = ws['G40']
        top_left_cell.value = str(despacho.consecutivo)

        ws.merge_cells('G77:J70')
        top_left_cell = ws['G77']
        top_left_cell.value = str(despacho.consecutivo)

        ws['B6'] = str(despacho.nombre_cliente)
        ws['D6'] = str(despacho.ciudad.nombre)
        ws['H6'] = str(despacho.pretty_fecha_envio_datetime())

        ws['B7'] = str(despacho.documento)
        ws['D7'] = str(despacho.direccion)
        ws['D7'] = str(despacho.direccion)

        if despacho.transportador != None and despacho.transportador != "":
            ws['B8'] = str(despacho.transportador)
        if despacho.conductor != None and despacho.conductor != "":
            ws['E8'] = str(despacho.conductor)
        if despacho.placa != None and despacho.placa != "":
            ws['J8'] = str(despacho.placa)

        i = 12
        contador = 1

        for sustraccion in sustracciones:


            ws['A' + str(i)] = contador
            ws['B' + str(i)] = sustraccion.producto.nombre
            ws['G' + str(i)] = sustraccion.cantidad
            ws['H' + str(i)] = str(str(sustraccion.producto.valor).replace('COL',''))
            ws['I' + str(i)] = str(str(sustraccion.producto.impuesto) + "%")
            ws['J' + str(i)] = str(sustraccion.pretty_print_valor_total())

            i += 1
            contador += 1
            if contador == 20:
                i = i + 16
            if contador == 22:
                i = i + 16

        total = sustracciones.aggregate(Sum('valor_total'))['valor_total__sum']
        total = "${:,.2f}".format(total)
        ws['J107'] = total

        ws['A105'] = despacho.observacion

        wb.save(output)

        filename = str(despacho.id) + '.xlsx'
        despacho.respaldo.save(filename, File(output))

    return "Reporte generado"