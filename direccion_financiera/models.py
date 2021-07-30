from djmoney.models.fields import MoneyField
from django.db import models
import uuid
from usuarios.models import User
from django.conf import settings
from pytz import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from direccion_financiera import tasks
from direccion_financiera import functions

settings_time_zone = timezone(settings.TIME_ZONE)

# Create your models here.

def upload_dinamic_dir_soporte_reporte(instance, filename):
    return '/'.join(['Reportes', str(instance.id), 'Formato interno', filename])

def upload_dinamic_dir_soporte_plano(instance, filename):
    return '/'.join(['Reportes', str(instance.id), 'Archivo plano', filename])

def upload_dinamic_dir_soporte_respaldo(instance, filename):
    return '/'.join(['Reportes', str(instance.id), 'Soporte respaldo', filename])

def upload_dinamic_dir_soporte_firma(instance, filename):
    return '/'.join(['Reportes', str(instance.id), 'Formato firmado', filename])

def upload_dinamic_dir_soporte_file_banco(instance, filename):
    return '/'.join(['Reportes', str(instance.id), 'Archivo banco', filename])

class Bancos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.IntegerField()
    nombre = models.CharField(max_length=50)
    longitud = models.CharField(max_length=100)

    def __str__(self):
        return str(self.codigo) + " - " + self.nombre

class Servicios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    descontable = models.BooleanField(default= False)

    def __str__(self):
        return self.nombre

class TipoSoporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    cuenta = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ConsecutivoReportes(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id)


class RubroPresupuestal(models.Model):
    nombre = models.CharField(max_length=500)

    def __str__(self):
        return self.nombre


class Reportes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.ForeignKey(ConsecutivoReportes, on_delete=models.DO_NOTHING, blank=True, null=True)
    number = models.BigIntegerField(blank=True,null=True)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_reporte", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_reporte",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    nombre = models.CharField(max_length=100)
    servicio = models.ForeignKey(Servicios, on_delete=models.DO_NOTHING)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.DO_NOTHING)
    rubro = models.ForeignKey(RubroPresupuestal, on_delete=models.DO_NOTHING, blank=True, null=True)
    tipo_soporte = models.ForeignKey(TipoSoporte, on_delete=models.DO_NOTHING)
    inicio = models.DateField()
    fin = models.DateField()

    file = models.FileField(upload_to=upload_dinamic_dir_soporte_reporte, blank=True, null=True)
    plano = models.FileField(upload_to=upload_dinamic_dir_soporte_plano, blank=True, null=True)

    respaldo = models.FileField(upload_to=upload_dinamic_dir_soporte_respaldo, blank=True, null=True)
    firma = models.FileField(upload_to=upload_dinamic_dir_soporte_firma, blank=True, null=True)
    file_banco = models.FileField(upload_to=upload_dinamic_dir_soporte_file_banco, blank=True, null=True)

    estado = models.CharField(max_length=100)

    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')

    efectivo = models.BooleanField(default=False)
    observacion = models.TextField(blank=True, null=True)


    numero_contrato = models.CharField(max_length=200,blank=True,null=True)
    numero_documento_equivalente = models.CharField(max_length=200,blank=True,null=True)


    def pretty_print_respaldo(self):
        try:
            url = self.respaldo.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.respaldo.name) +'</a>'

    def pretty_print_firma(self):
        try:
            url = self.firma.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.firma.name) +'</a>'

    def pretty_print_file_banco(self):
        try:
            url = self.file_banco.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file_banco.name) +'</a>'

    def url_respaldo(self):
        url = None
        try:
            url = self.respaldo.url
        except:
            pass
        return url

    def url_file_banco(self):
        url = None
        try:
            url = self.file_banco.url
        except:
            pass
        return url

    def url_firma(self):
        url = None
        try:
            url = self.firma.url
        except:
            pass
        return url

    def url_file_banco(self):
        url = None
        try:
            url = self.file_banco.url
        except:
            pass
        return url

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_plano(self):
        url = None
        try:
            url = self.plano.url
        except:
            pass
        return url

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_update_datetime_datetime(self):
        return self.update_datetime.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def reporte_update_datetime(self):
        return self.update_datetime.astimezone(settings_time_zone).strftime('%d/%m/%Y')

    def reporte_inicio_datetime(self):
        return self.inicio.strftime('%d/%m/%Y')

    def reporte_fin_datetime(self):
        return self.fin.strftime('%d/%m/%Y')

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def pretty_print_valor_descuentos(self):

        valor_bruto = self.valor

        for pago in Pagos.objects.filter(reporte__id=self.id):
            for descuento in Descuentos.objects.filter(pago = pago):
                valor_bruto -= descuento.valor

        for amortizacion in Amortizaciones.objects.filter(pago_descontado__reporte__id=self.id):
            valor_bruto -= amortizacion.valor

        return str(valor_bruto).replace('COL','')

    def valor_descuentos(self):

        valor_bruto = self.valor

        for pago in Pagos.objects.filter(reporte__id=self.id):
            for descuento in Descuentos.objects.filter(pago=pago):
                valor_bruto -= descuento.valor

            for amortizacion in Amortizaciones.objects.filter(pago_descontado=pago):
                valor_bruto -= amortizacion.valor

        return valor_bruto

class Pagos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_pago", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_pago", on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    reporte = models.ForeignKey(Reportes, on_delete=models.DO_NOTHING)
    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')
    tercero = models.ForeignKey(to='recursos_humanos.Contratistas', on_delete=models.DO_NOTHING)
    observacion = models.TextField(max_length=500)

    estado = models.CharField(max_length=100)
    notificado = models.BooleanField(default=False)
    publico = models.BooleanField(default = True)
    cuotas = models.IntegerField(blank=True, null=True)

    descuentos_pendientes = models.TextField(blank=True, null=True)
    descuentos_pendientes_otro_valor = models.TextField(blank=True, null=True)

    tipo_cuenta = models.CharField(max_length=500, blank=True, null=True)
    banco = models.CharField(max_length=500, blank=True, null=True)
    cuenta = models.CharField(max_length=500, blank=True, null=True)
    cargo = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.valor)

    def get_rubro(self):
        rubro = ''
        if self.reporte.rubro != None:
            rubro = self.reporte.rubro.nombre
        return rubro

    def get_initial_amortizaciones(self):
        inicial = {}
        return inicial

    def get_list_descuentos(self):
        list_descuentos = [0, 0, 0, 0, 0]

        i = 0
        for descuento in Descuentos.objects.filter(pago__id=self.id):
            list_descuentos[i] = descuento.valor.amount.__float__()
            i += 1

        return list_descuentos

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def chart_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y')

    def pretty_update_datetime_datetime(self):
        return self.update_datetime.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_print_valor(self):
        return str(self.valor).replace('COL', '')

    def pretty_print_valor_descuentos(self):

        valor_bruto = self.valor

        for descuento in Descuentos.objects.filter(pago=self):
            valor_bruto -= descuento.valor

        for amortizacion in Amortizaciones.objects.filter(pago_descontado=self):
            valor_bruto -= amortizacion.valor

        return str(valor_bruto).replace('COL', '')

    def valor_descuentos(self):

        valor_bruto = self.valor

        for descuento in Descuentos.objects.filter(pago=self):
            valor_bruto -= descuento.valor

        for amortizacion in Amortizaciones.objects.filter(pago_descontado=self):
            valor_bruto -= amortizacion.valor

        return valor_bruto

    def valor_descuentos_amount(self):

        valor_bruto = self.valor

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            valor_bruto -= descuento.valor

        return valor_bruto.amount

    def pretty_print_valor_solo_descuentos(self):

        valor = 0

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            valor += descuento.valor

        return str(valor).replace('COL', '')

    def pretty_print_valor_solo_amortizaciones(self):

        data = '<p>Amortizaciones descontadas</p>'
        for amortizacion in Amortizaciones.objects.filter(pago_descontado__id=self.id):
            data += '<p>{0} - Estado: {1}, Reporte {2}</p>'.format(
                str(amortizacion.valor).replace('COL', ''),
                amortizacion.estado,
                amortizacion.pago.reporte.consecutivo
            )
        return data

    def valor_solo_descuentos(self):

        valor = 0

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            valor += descuento.valor

        return valor

    def valor_solo_descuentos_amount(self):

        valor = 0

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            valor += descuento.valor

        if valor == 0:
            return valor
        else:
            return valor.amount

    def solo_descuentos_tooltip(self):

        value = ''

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            value += descuento.concepto + ': ' + descuento.pretty_print_valor() + ' - ' + descuento.observacion + ', '

        return value[:-2]

    def descuentos_chart(self):

        value = 0

        for descuento in Descuentos.objects.filter(pago__id=self.id):
            value += descuento.valor.amount.__float__()

        for amortizacion in Amortizaciones.objects.filter(pago_descontado=self):
            value += amortizacion.valor.amount.__float__()

        return value

    def observacion_pretty(self):

        if not self.reporte.servicio.descontable:

            descuentos = ''
            amortizaciones = ''

            for descuento in Descuentos.objects.filter(pago__id=self.id):
                descuentos += descuento.concepto + ': ' + descuento.pretty_print_valor() + ' - ' + descuento.observacion + '\n'

            for amortizacion in Amortizaciones.objects.filter(pago_descontado=self):
                amortizaciones += 'Amortización # {1} - {0}, Reporte: {2}\n'.format(
                    amortizacion.pretty_print_valor(),
                    amortizacion.consecutivo,
                    amortizacion.pago.reporte.consecutivo
                )

            if descuentos == '':
                descuentos = 'N/A'

            if amortizaciones == '':

                observacion = self.observacion + '\nValor inicial: ' + self.pretty_print_valor() + '\nDescuentos:\n' + \
                              descuentos
            else:
                observacion = self.observacion + '\nValor inicial: ' + self.pretty_print_valor() + '\nDescuentos:\n' + \
                              descuentos + amortizaciones[:-1]

            return observacion

        else:
            observacion = self.observacion + '\nValor inicial: ' + self.pretty_print_valor() + '\nCuotas: ' + str(self.cuotas)

            return observacion

    def descuentos_html(self):
        descuentos = ''

        i = 1
        for descuento in Descuentos.objects.filter(pago__id=self.id):
            descuentos += '<p><span style="font-weight:bold;">' + str(
                i) + ' - </span>' + descuento.concepto + ': ' + descuento.pretty_print_valor() + ' - ' + descuento.observacion + '</p>'
            i += 1

        for amortizacion in Amortizaciones.objects.filter(pago_descontado = self):
            descuentos += '<p><span style="font-weight:bold;">{0}</span> - Amortización #{1} reporte {2}: {3}</p>'.format(
                i,
                amortizacion.consecutivo,
                amortizacion.pago.reporte.consecutivo,
                amortizacion.pretty_print_valor()
            )
            i += 1

        return descuentos

    def get_amortizacion_html(self):
        data = '<p>Amortización</p>'
        if Amortizaciones.objects.filter(pago=self).count() > 0:
            for amortizacion in Amortizaciones.objects.filter(pago = self).order_by('consecutivo'):
                if amortizacion.estado == 'Asignada' or amortizacion.estado == 'Descontada':
                    data += '<p>{0}: {1} en el reporte {2}</p>'.format(
                        str(amortizacion.valor).replace('COL', ''),
                        amortizacion.estado,
                        amortizacion.pago_descontado.reporte.consecutivo
                    )
                else:
                    data += '<p>{0}: {1}</p>'.format(str(amortizacion.valor).replace('COL',''), amortizacion.estado)
        else:
            data += '<p>{0} cuota(s) de {1}</p>'.format(self.cuotas,'${:20,.2f}'.format(self.valor.amount/self.cuotas))
        return data

    def get_fecha_ultimo_descuento(self):
        if self.reporte.servicio.descontable:
            amortizaciones = Amortizaciones.objects.filter(pago = self, estado = "Descontada").exclude(fecha_descontado = None).order_by('-fecha_descontado')
            primera = amortizaciones.first()
            if primera != None:
                primera.pretty_update_datetime_datetime()
            else:
                return ''
        else:
            return 'No es un pago descontable'

    def get_cantidad_amortizaciones_pendientes(self):
        if self.reporte.servicio.descontable:
            amortizaciones = Amortizaciones.objects.filter(pago = self).filter(estado = 'Pendiente')
            return amortizaciones.count()
        else:
            return 0

class Amortizaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    pago = models.ForeignKey(Pagos, on_delete=models.DO_NOTHING, related_name="pago_amortizacion")
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP')

    estado = models.CharField(max_length=100)
    pago_descontado = models.ForeignKey(Pagos, on_delete=models.DO_NOTHING, blank=True, null=True)
    fecha_descontado = models.DateTimeField(blank=True, null=True)

    consecutivo = models.IntegerField()
    disabled = models.BooleanField(default=True)

    def get_pago_completo(self):
        estado = True

        for amortizacion in Amortizaciones.objects.filter(pago = self.pago):
            if amortizacion.estado != 'Descontada':
                estado = False
        return estado

    def pretty_print_valor(self):
        return str(self.valor).replace('COL', '')

    def get_dict_pago_descontado(self):
        return {}

    def pretty_update_datetime_datetime(self):
        if self.fecha_descontado == None:
            return ''
        else:
            return self.fecha_descontado.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def get_checked(self, id):
        if self.estado == 'Asignada' or self.estado == 'Descontada':
            return 'checked'
        else:
            return ''

    def get_disabled(self, id):

        if self.disabled:
            disabled = 'disabled'
        else:
            if self.estado == 'Asignada':
                if str(self.pago_descontado.id) != str(id):
                    disabled = 'disabled'
                else:
                    disabled = ''
            else:
                disabled = ''

        return disabled

    def get_descripcion(self, id):
        descripcion = ''

        if self.estado == 'Asignada' or self.estado == 'Descontada':
            if str(self.pago_descontado.id) != str(id):
                descripcion = ' - {0} en el reporte {1}'.format(
                    self.estado,
                    self.pago_descontado.reporte.consecutivo
                )
            else:
                descripcion = ' - {0} en este reporte'.format(
                    self.estado
                )

        return descripcion


    def get_descripcion_no_id(self):
        descripcion = ''

        if self.estado == 'Asignada' or self.estado == 'Descontada':
            descripcion = '{0} en el reporte {1}'.format(
                self.estado,
                self.pago_descontado.reporte.consecutivo
            )
        else:
            descripcion = self.estado


        return descripcion

class Descuentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="descuentos_usuario_creacion_pago", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="descuentos_usuario_actualizacion_pago", on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    pago = models.ForeignKey(Pagos, on_delete=models.DO_NOTHING)

    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')
    concepto = models.TextField(max_length=500)
    observacion = models.TextField(max_length=500)


    def __str__(self):
        return str(self.valor)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_update_datetime_datetime(self):
        return self.update_datetime.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

#@receiver(post_save, sender=Pagos)
#@receiver(post_delete, sender=Pagos)
#def PagoUpdate(sender, instance, **kwargs):
#    if instance.estado == 'Pago creado':
#        valor = 0
#        for pago in Pagos.objects.filter(reporte=instance.reporte):
#            valor += pago.valor

#        reporte = instance.reporte
#        reporte.valor = valor
#        reporte.save()

#        reporte.file.delete(save=True)
#        reporte.plano.delete(save=True)

#        tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)
#        functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)

@receiver(post_save, sender=Reportes)
def ReportesUpdate(sender, instance, **kwargs):
    if instance.firma.name != None and instance.firma.name != '':
        if instance.file_banco.name != None and instance.file_banco.name != '':
            Reportes.objects.filter(id=instance.id).update(estado='Completo')
        #else:
        #    Reportes.objects.filter(id = instance.id).update(estado = 'Reportado')
        #    Pagos.objects.filter(reporte = instance).update(estado = 'Reportado')