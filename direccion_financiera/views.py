import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from direccion_financiera import forms, models
from recursos_humanos import models as rh_models
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from direccion_financiera.tasks import send_mail_templated_pago, send_mail_templated_reporte
from direccion_financiera import tasks
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_DIRECCION_FINANCIERA
from reportes.models import Reportes
import json
from desplazamiento.models import Desplazamiento, Solicitudes
from desplazamiento.forms import DesplazamientoForm, FinancieraSolicitudForm
from direccion_financiera import functions
from django.utils import timezone
# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class DireccionFinancieraOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/lista.html'
    permissions = {
        "all": ["usuarios.direccion_financiera.ver"]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(DireccionFinancieraOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.direccion_financiera.bancos.ver'):
            items.append({
                'sican_categoria': 'Bancos',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'bancos/',
                'sican_name': 'Bancos',
                'sican_icon': 'account_balance',
                'sican_description': 'Nombre y códigos de las entidades bancarias'
            })

        if self.request.user.has_perm('usuarios.direccion_financiera.terceros.ver'):
            items.append({
                'sican_categoria': 'Terceros',
                'sican_color': 'orange darken-4',
                'sican_order': 2,
                'sican_url': 'terceros/',
                'sican_name': 'Terceros',
                'sican_icon': 'art_track',
                'sican_description': 'Información general para el registro y gestión de contratistas'
            })

        if self.request.user.has_perm('usuarios.direccion_financiera.reportes.ver'):
            items.append({
                'sican_categoria': 'Reportes de pago',
                'sican_color': 'brown darken-4',
                'sican_order': 3,
                'sican_url': 'reportes/',
                'sican_name': 'Reportes',
                'sican_icon': 'monetization_on',
                'sican_description': 'Reporte y notificación de pagos a terceros'
            })

        if self.request.user.has_perm('usuarios.direccion_financiera.consulta_pagos.ver'):
            items.append({
                'sican_categoria': 'Consulta de pagos',
                'sican_color': 'purple darken-4',
                'sican_order': 4,
                'sican_url': 'consulta_pagos/',
                'sican_name': 'Pagos',
                'sican_icon': 'monetization_on',
                'sican_description': 'Consulta y reportes de pagos a terceros'
            })


        if self.request.user.has_perm('usuarios.direccion_financiera.solicitudes_desplazamiento.ver'):
            items.append({
                'sican_categoria': 'Desplazamiento',
                'sican_color': 'pink darken-4',
                'sican_order': 5,
                'sican_url': 'solicitudes_desplazamiento/',
                'sican_name': 'Desplazamiento',
                'sican_icon': 'map',
                'sican_description': 'Solicitudes de desplazamiento a sedes educativas y municipios.'
            })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Dirección financiera"
        kwargs['items'] = self.get_items()
        return super(DireccionFinancieraOptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------------ BANCOS --------------------------------------

class BancosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.bancos.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/bancos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "bancos"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/bancos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.direccion_financiera.bancos.crear')
        return super(BancosListView,self).get_context_data(**kwargs)


class BancosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.bancos.ver",
            "usuarios.direccion_financiera.bancos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/bancos/crear.html'
    form_class = forms.BancoForm
    success_url = "../"
    model = models.Bancos

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR BANCO"
        return super(BancosCreateView,self).get_context_data(**kwargs)


class BancosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.bancos.ver",
            "usuarios.direccion_financiera.bancos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/bancos/editar.html'
    form_class = forms.BancoForm
    success_url = "../../"
    model = models.Bancos


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR BANCO"
        kwargs['breadcrum_active'] = models.Bancos.objects.get(id=self.kwargs['pk']).nombre
        return super(BancosUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------------ TERCEROS ------------------------------------

class TercerosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.terceros.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/terceros/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "terceros"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/terceros/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.direccion_financiera.terceros.crear')
        return super(TercerosListView,self).get_context_data(**kwargs)

class TercerosReporteListadoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Listado de terceros e inforación general',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_listado_terceros.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')

class TercerosTerceroPagosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
            "usuarios.direccion_financiera.descuentos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/terceros/descuentos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "PAGOS DE TERCEROS"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/terceros/pagos/' + str(self.kwargs['pk'])
        kwargs['breadcrum_active'] = rh_models.Contratistas.objects.get(pk = kwargs['pk']).fullname()
        kwargs['consulta_dinamica'] = models.Pagos.objects.filter(tercero_id=self.kwargs['pk']).count() > 0
        return super(TercerosTerceroPagosListView,self).get_context_data(**kwargs)

class TerceroPagosReporteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        tercero = rh_models.Contratistas.objects.get(id = self.kwargs['pk'])

        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Reporte de pagos y descuentos ' + tercero.fullname() + ' - ' + str(tercero.cedula),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_listado_tercero_especifico.delay(reporte.id,tercero.id)

        return HttpResponseRedirect('/reportes/')


class SolicitudesDesplazamientoReporteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Acumulado solicitudes de desplazamiento',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_listado_solicitudes.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')

class TerceroPagosDinamicaView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        TemplateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/terceros/descuentos/consulta_dinamica.html'

    def get_context_data(self, **kwargs):
        contratista = rh_models.Contratistas.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "CONSULTA DINAMICA DE PAGOS"
        kwargs['breadcrum_active'] = contratista.fullname()
        kwargs['pk_str'] = self.kwargs['pk']
        kwargs['years'] = json.dumps(contratista.get_years_pagos())
        return super(TerceroPagosDinamicaView,self).get_context_data(**kwargs)



class TercerosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
            "usuarios.direccion_financiera.terceros.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/terceros/crear.html'
    form_class = forms.TerceroForm
    success_url = "../"
    model = rh_models.Contratistas

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.usuario_creacion = self.request.user
        self.object.save()
        return super(TercerosCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR TERCERO"
        return super(TercerosCreateView,self).get_context_data(**kwargs)


class TercerosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.terceros.ver",
            "usuarios.direccion_financiera.terceros.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/terceros/editar.html'
    form_class = forms.TerceroForm
    success_url = "../../"
    model = rh_models.Contratistas


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR TERCERO"
        kwargs['breadcrum_active'] = rh_models.Contratistas.objects.get(id=self.kwargs['pk']).fullname
        return super(TercerosUpdateView,self).get_context_data(**kwargs)
#----------------------------------------------------------------------------------

#------------------------------------ REPORTES ------------------------------------

class ReportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.reportes.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "reportes de pago"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/reportes/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.direccion_financiera.reportes.crear')
        kwargs['permiso_informe'] = self.request.user.has_perm('usuarios.direccion_financiera.reportes.informe')
        return super(ReportesListView,self).get_context_data(**kwargs)


class InformePagosView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.informe",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Informe acumulativo reportes de pago',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_reporte_pagos.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')


class ReportesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/crear.html'
    form_class = forms.ReporteForm
    success_url = "../"
    model = models.Reportes

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.usuario_creacion = self.request.user
        self.object.usuario_actualizacion = self.request.user
        self.object.estado = 'Carga de pagos'
        self.object.valor = 0
        self.object.consecutivo = models.ConsecutivoReportes.objects.create()
        self.object.save()
        return super(ReportesCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR REPORTE"
        kwargs['respaldo_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['firma_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        return super(ReportesCreateView,self).get_context_data(**kwargs)


class ReportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/editar.html'
    form_class = forms.ReporteUpdateForm
    success_url = "../../"
    model = models.Reportes

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.usuario_actualizacion = self.request.user
        self.object.save()
        return super(ReportesUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTUALIZAR REPORTE DE PAGO"
        kwargs['breadcrum_active'] = reporte.nombre
        kwargs['respaldo_url'] = reporte.pretty_print_respaldo()
        kwargs['firma_url'] = reporte.pretty_print_firma()
        kwargs['show'] = True if reporte.firma.name != '' and reporte.estado != 'Completo' else False
        kwargs['show_reportar'] = True if reporte.firma.name != '' and reporte.estado != 'Reportado' and reporte.estado != 'En pagaduria' and reporte.estado != 'Completo' else False
        kwargs['show_reporte_enviado'] = True if self.request.user.is_superuser and reporte.estado == 'Reportado' else False
        kwargs['show_resultado'] = True if reporte.firma.name != '' and reporte.estado == 'En pagaduria' else False
        return super(ReportesUpdateView,self).get_context_data(**kwargs)


class ReportesResultadoUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/resultado.html'
    form_class = forms.ResultadoReporteForm
    success_url = "../../../"
    model = models.Reportes

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        self.object = form.save()

        for pago in models.Pagos.objects.filter(reporte__id = self.kwargs['pk']):
            estado = form.cleaned_data[str(pago.id)]

            if pago.estado != estado:
                pago.estado = estado
                pago.save()

                if form.cleaned_data['reportar_'+str(pago.id)]:

                    url_base = self.request.META['HTTP_ORIGIN']
                    cuenta = pago.tercero.cuenta
                    hide = ''

                    for val in range(3, len(cuenta) - 5):
                        hide += '*'

                    tercero = pago.tercero

                    send_mail_templated_pago.delay(str(pago.id),'mail/direccion_financiera/reportes/pagos/reporte_pago.tpl',
                                              {
                                                  'url_base': url_base,
                                                  'first_name': tercero.nombres,
                                                  'estado': estado,
                                                  'cuenta': cuenta[:4] + hide + cuenta[len(cuenta) - 4:],
                                                  'banco': tercero.banco.nombre,
                                                  'tipo_cuenta': tercero.tipo_cuenta,
                                                  'valor': pago.pretty_print_valor_descuentos()
                                              },
                                              DEFAULT_FROM_EMAIL,
                                              [pago.tercero.email, EMAIL_HOST_USER])


        return super(ReportesResultadoUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "RESULTADO REPORTE DE PAGO"
        kwargs['breadcrum_active'] = reporte.nombre
        kwargs['file_banco_url'] = reporte.pretty_print_file_banco()
        return super(ReportesResultadoUpdateView,self).get_context_data(**kwargs)


class ReporteReportesView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../../"
    form_class = forms.ReportarReporteForm
    template_name = 'direccion_financiera/reportes/reporte.html'

    def dispatch(self, request, *args, **kwargs):
        if models.Reportes.objects.get(id=self.kwargs['pk']).estado == 'Reportado':
            return HttpResponseRedirect('../')
        else:
            return super(ReporteReportesView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['breadcrum_active'] = models.Reportes.objects.get(id=self.kwargs['pk']).nombre
        return super(ReporteReportesView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])

        if reporte.estado != 'Reportado':

            if reporte.servicio.descontable:
                for pago in models.Pagos.objects.filter(reporte=reporte):
                    valor = pago.valor.amount/pago.cuotas
                    for i in range(0,pago.cuotas):
                        amortizacion = models.Amortizaciones.objects.create(
                            pago = pago,
                            valor = valor,
                            estado = 'Pendiente',
                            consecutivo = i+1
                        )

                        if i == 0:
                            amortizacion.disabled = False
                            amortizacion.save()


            if reporte.efectivo:
                adjuntos = [
                    ('PAGO ' + str(reporte.consecutivo.id) + ' - REPORTE FIRMADO.' + str(reporte.firma.name.split('.')[-1]), reporte.firma.read(),
                     mimetypes.guess_type(reporte.firma.name)[0])
                ]

            else:

                adjuntos = [
                    ('PAGO '+ str(reporte.consecutivo.id) + ' - REPORTE FIRMADO.' + str(reporte.firma.name.split('.')[-1]), reporte.firma.read(),
                     mimetypes.guess_type(reporte.firma.name)[0]),
                    ('PAGO ' + str(reporte.consecutivo.id) + ' - ARCHIVO PLANO.' + str(reporte.plano.name.split('.')[-1]), reporte.plano.read(),
                     mimetypes.guess_type(reporte.plano.name)[0])
                ]

            if reporte.respaldo.name != '':
                template = 'mail/direccion_financiera/reportes/reporte.tpl'
            else:
                template = 'mail/direccion_financiera/reportes/reporte_sin_respaldo.tpl'

            send_mail_templated_reporte(
                template,
                {
                    'url_base': 'http://' + self.request.META['HTTP_HOST'],
                    'nombre_reporte': str(reporte.consecutivo.id) + ' - ' + reporte.nombre,
                    'valor': reporte.pretty_print_valor_descuentos(),
                    'proyecto': reporte.proyecto.nombre,
                    'respaldo': 'http://' + self.request.META['HTTP_HOST'] + str(reporte.url_respaldo()),
                    'usuario': reporte.usuario_actualizacion.get_full_name_string()
                },
                DEFAULT_FROM_EMAIL,
                [self.request.user.email, EMAIL_HOST_USER, form.cleaned_data['email']],
                attachments=adjuntos
            )

            models.Reportes.objects.filter(id=self.kwargs['pk']).update(estado='Reportado')
            models.Pagos.objects.filter(reporte=reporte).update(estado='Reportado')

            for amortizacion in models.Amortizaciones.objects.filter(estado = 'Asignada', pago_descontado__in = models.Pagos.objects.filter(reporte = reporte)):
                amortizacion.estado = 'Descontada'
                amortizacion.disabled = True
                amortizacion.save()

                try:
                    siguiente = models.Amortizaciones.objects.get(estado = 'Pendiente',pago = amortizacion.pago,consecutivo = amortizacion.consecutivo + 1)
                except:
                    pass
                else:
                    siguiente.disabled = False
                    siguiente.save()

        return HttpResponseRedirect(self.get_success_url())

class ReporteEnvioView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../../"

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.is_superuser:
            models.Reportes.objects.filter(id = self.kwargs['pk']).update(estado = 'En pagaduria')
            models.Pagos.objects.filter(reporte__id = self.kwargs['pk']).update(estado='En pagaduria')

        return HttpResponseRedirect('../../../')


class ReportesDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.eliminar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])

        if reporte.estado == 'Carga de pagos':

            for pago in models.Pagos.objects.filter(reporte=reporte):
                models.Amortizaciones.objects.filter(pago_descontado=pago).update(estado='Pendiente',pago_descontado=None)
                models.Descuentos.objects.filter(pago = pago).delete()
                pago.delete()

            reporte.delete()

        return HttpResponseRedirect('../../')

#----------------------------------------------------------------------------------

#-------------------------------------- PAGOS -------------------------------------

class PagosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.reportes.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/pagos/lista.html'


    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "reportes de pago"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/reportes/pagos/' + str(self.kwargs['pk'])
        kwargs['permiso_crear'] = False if reporte.estado != 'Carga de pagos' else self.request.user.has_perm('usuarios.direccion_financiera.reportes.crear')
        kwargs['breadcrum_active'] = reporte.nombre
        kwargs['show'] = True if reporte.file.name != '' or reporte.plano.name != '' else False
        kwargs['file'] = reporte.url_file()
        kwargs['plano'] = reporte.url_plano()
        return super(PagosListView,self).get_context_data(**kwargs)


class PagosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/pagos/crear.html'
    success_url = "../"

    def get_form_class(self):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])

        if reporte.servicio.descontable:
            return forms.PagoDescontableForm
        else:
            return forms.PagoForm

    def get_initial(self):
        return {
            'pk': self.kwargs['pk']
        }

    def form_valid(self, form):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])


        if reporte.servicio.descontable:
            pago = models.Pagos.objects.create(
                usuario_creacion = self.request.user,
                usuario_actualizacion = self.request.user,
                reporte = models.Reportes.objects.get(id = self.kwargs['pk']),
                valor = float(form.cleaned_data['valor'].replace('$ ','').replace(',','')),
                tercero = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']),
                observacion = form.cleaned_data['observacion'],
                estado = 'Pago creado',
                publico=form.cleaned_data['publico'],
                cuotas=form.cleaned_data['cuotas'],
            )

            try:
                pago.tipo_cuenta = pago.tercero.tipo_cuenta
                pago.banco = pago.tercero.banco.nombre
                pago.cuenta = pago.tercero.cuenta
                pago.cargo = pago.tercero.cargo.nombre
                pago.save()
            except:
                pass

            valor = 0
            for pago_obj in models.Pagos.objects.filter(reporte=pago.reporte):
                valor += pago_obj.valor

            reporte = pago.reporte
            reporte.valor = valor
            reporte.save()

            reporte.file.delete(save=True)
            reporte.plano.delete(save=True)

            tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)
            if not reporte.efectivo:
                functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)

        else:

            descuentos_pendientes = json.loads(form.cleaned_data.get("descuentos_pendientes"))
            descuentos_pendientes_otro_valor = json.loads(form.cleaned_data.get("descuentos_pendientes_otro_valor"))

            pago_new = models.Pagos.objects.create(
                usuario_creacion=self.request.user,
                usuario_actualizacion=self.request.user,
                reporte=models.Reportes.objects.get(id=self.kwargs['pk']),
                valor=float(form.cleaned_data['valor'].replace('$ ', '').replace(',', '')),
                tercero=rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']),
                observacion=form.cleaned_data['observacion'],
                estado='Pago creado',
                publico=form.cleaned_data['publico'],
                descuentos_pendientes=form.cleaned_data['descuentos_pendientes'],
                descuentos_pendientes_otro_valor=form.cleaned_data['descuentos_pendientes_otro_valor'],
            )

            try:
                pago_new.tipo_cuenta = pago_new.tercero.tipo_cuenta
                pago_new.banco = pago_new.tercero.banco.nombre
                pago_new.cuenta = pago_new.tercero.cuenta
                pago_new.cargo = pago_new.tercero.cargo.nombre
                pago_new.save()
            except:
                pass

            for i in range(1,6):

                uuid_descuento = form.cleaned_data.get("uuid_descuento_" + str(i))
                valor_descuento = form.cleaned_data.get("valor_descuento_" + str(i))
                concepto_descuento = form.cleaned_data.get("concepto_descuento_" + str(i))
                observacion_descuento = form.cleaned_data.get("observacion_descuento_" + str(i))

                if valor_descuento != '' and valor_descuento != None:
                    models.Descuentos.objects.create(
                        usuario_creacion=self.request.user,
                        usuario_actualizacion=self.request.user,
                        pago = pago_new,
                        valor = float(valor_descuento.replace('$ ','').replace(',','')),
                        concepto = concepto_descuento,
                        observacion = observacion_descuento
                    )


            for key in descuentos_pendientes.keys():
                pago = models.Pagos.objects.get(id=key)
                for key2 in descuentos_pendientes[key]:
                    amortizacion = models.Amortizaciones.objects.get(id=key2)
                    if descuentos_pendientes[key][key2]['descontar']:
                        amortizacion.pago_descontado = pago_new
                        amortizacion.fecha_descontado = timezone.now()
                        amortizacion.estado = 'Asignada'
                        amortizacion.save()

            valor = 0
            for pago_obj in models.Pagos.objects.filter(reporte=pago_new.reporte):
                valor += pago_obj.valor

            reporte = pago_new.reporte
            reporte.valor = valor
            reporte.save()

            reporte.file.delete(save=True)
            reporte.plano.delete(save=True)

            tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)

            if not reporte.efectivo:
                functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)

        return super(PagosCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "CREAR PAGO"
        kwargs['breadcrum_1'] = models.Reportes.objects.get(id=self.kwargs['pk']).nombre
        kwargs['reporte'] = reporte

        return super(PagosCreateView,self).get_context_data(**kwargs)


class PagosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/pagos/editar.html'
    success_url = "../../"

    def get_form_class(self):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])

        if reporte.servicio.descontable:
            return forms.PagoDescontableForm
        else:
            return forms.PagoForm

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_pago': self.kwargs['pk_pago']
        }

    def form_valid(self, form):

        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])

        if reporte.servicio.descontable:

            pago = models.Pagos.objects.get(id = self.kwargs['pk_pago'])
            pago.usuario_actualizacion = self.request.user
            pago.valor = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))
            pago.tercero = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula'])
            pago.observacion = form.cleaned_data['observacion']
            pago.publico = form.cleaned_data['publico']
            pago.cuotas = form.cleaned_data['cuotas']
            pago.save()

            try:
                pago.tipo_cuenta = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).tipo_cuenta
                pago.banco = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).banco.nombre
                pago.cuenta = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).cuenta
                pago.cargo = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).cargo.nombre
                pago.save()
            except:
                pass

            valor = 0
            for pago_obj in models.Pagos.objects.filter(reporte=pago.reporte):
                valor += pago_obj.valor

            reporte = pago.reporte
            reporte.valor = valor
            reporte.save()

            reporte.file.delete(save=True)
            reporte.plano.delete(save=True)

            tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)
            if not reporte.efectivo:
                functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)


        else:

            pago = models.Pagos.objects.get(id=self.kwargs['pk_pago'])
            models.Amortizaciones.objects.filter(pago_descontado = pago, estado = 'Asignada').update(
                pago_descontado = None,
                estado = 'Pendiente'
            )

            descuentos_pendientes = json.loads(form.cleaned_data.get("descuentos_pendientes"))
            descuentos_pendientes_otro_valor = json.loads(form.cleaned_data.get("descuentos_pendientes_otro_valor"))


            pago.usuario_actualizacion = self.request.user
            pago.valor = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))
            pago.tercero = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula'])
            pago.observacion = form.cleaned_data['observacion']
            pago.publico = form.cleaned_data['publico']
            pago.descuentos_pendientes = form.cleaned_data['descuentos_pendientes']
            pago.descuentos_pendientes_otro_valor = form.cleaned_data['descuentos_pendientes_otro_valor']
            pago.save()

            try:
                pago.tipo_cuenta = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).tipo_cuenta
                pago.banco = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).banco.nombre
                pago.cuenta = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).cuenta
                pago.cargo = rh_models.Contratistas.objects.get(cedula=form.cleaned_data['cedula']).cargo.nombre
                pago.save()
            except:
                pass


            for i in range(1,6):

                uuid_descuento = form.cleaned_data.get("uuid_descuento_" + str(i))
                valor_descuento = form.cleaned_data.get("valor_descuento_" + str(i))
                concepto_descuento = form.cleaned_data.get("concepto_descuento_" + str(i))
                observacion_descuento = form.cleaned_data.get("observacion_descuento_" + str(i))

                if uuid_descuento == None:
                    if valor_descuento != '' or concepto_descuento != '' or observacion_descuento != '':
                        models.Descuentos.objects.create(
                            usuario_creacion=self.request.user,
                            usuario_actualizacion=self.request.user,
                            pago=pago,
                            valor=float(valor_descuento.replace('$ ', '').replace(',', '')),
                            concepto=concepto_descuento,
                            observacion=observacion_descuento
                        )

                    else:
                        pass

                else:
                    if valor_descuento != '' or concepto_descuento != '' or observacion_descuento != '':
                        models.Descuentos.objects.filter(id=uuid_descuento).update(
                            valor = float(valor_descuento.replace('$ ', '').replace(',', '')),
                            concepto = concepto_descuento,
                            observacion = observacion_descuento
                        )
                    else:
                        models.Descuentos.objects.filter(id=uuid_descuento).delete()


            for key in descuentos_pendientes.keys():
                pago_json = models.Pagos.objects.get(id=key)
                for key2 in descuentos_pendientes[key]:
                    amortizacion = models.Amortizaciones.objects.get(id=key2)
                    if descuentos_pendientes[key][key2]['descontar']:
                        amortizacion.pago_descontado = pago
                        amortizacion.fecha_descontado = timezone.now()
                        amortizacion.estado = 'Asignada'
                        amortizacion.save()


            valor = 0
            for pago_obj in models.Pagos.objects.filter(reporte=pago.reporte):
                valor += pago_obj.valor

            reporte = pago.reporte
            reporte.valor = valor
            reporte.save()

            reporte.file.delete(save=True)
            reporte.plano.delete(save=True)

            tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)
            if not reporte.efectivo:
                functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)

        return super(PagosUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        kwargs['reporte'] = reporte
        pago = models.Pagos.objects.get(id=self.kwargs['pk_pago'])
        kwargs['title'] = "ACTUALIZAR PAGO"
        kwargs['breadcrum_1'] = models.Reportes.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active'] = pago.tercero.fullname()
        kwargs['tipo_cuenta'] = pago.tercero.tipo_cuenta
        kwargs['banco'] = pago.tercero.banco.nombre
        kwargs['cuenta'] = pago.tercero.cuenta
        kwargs['url_descontables'] = '/rest/v1.0/direccion_financiera/pagos/{0}/'.format(pago.id)
        kwargs['cedula'] = pago.tercero.cedula
        kwargs['pago'] = pago
        return super(PagosUpdateView,self).get_context_data(**kwargs)


class PagosDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.eliminar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])
        pago = models.Pagos.objects.get(id = self.kwargs['pk_pago'])

        models.Amortizaciones.objects.filter(pago_descontado = pago).update(estado = 'Pendiente', pago_descontado = None)

        if pago.estado == 'Pago creado' and pago.reporte == reporte:
            for descuento in models.Descuentos.objects.filter(pago = pago):
                descuento.delete()
            pago.delete()

        valor = 0
        for pago_obj in models.Pagos.objects.filter(reporte=reporte):
            valor += pago_obj.valor

        reporte = pago.reporte
        reporte.valor = valor
        reporte.save()

        reporte.file.delete(save=True)
        reporte.plano.delete(save=True)

        tasks.build_reporte_interno(str(reporte.id), reporte.usuario_actualizacion.email)
        functions.build_archivo_plano(str(reporte.id), reporte.usuario_actualizacion.email)

        return HttpResponseRedirect('../../')


class AmortizacionesPagosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.reportes.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/pagos/amortizaciones/lista.html'


    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id = self.kwargs['pk'])
        pago = models.Pagos.objects.get(id = self.kwargs['pk_pago'])
        kwargs['title'] = "AMORTIZACIONES"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/reportes/pagos/{0}/amortizaciones/{1}/'.format(
            self.kwargs['pk'],
            self.kwargs['pk_pago']
        )
        kwargs['breadcrum_1'] = reporte.nombre
        kwargs['breadcrum_active'] = pago.tercero.get_full_name()
        return super(AmortizacionesPagosListView,self).get_context_data(**kwargs)


class AmortizacionesPagosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):
    permissions = {
        "all": [
            "usuarios.direccion_financiera.reportes.ver",
            "usuarios.direccion_financiera.reportes.editar",
            "usuarios.direccion_financiera.reportes.amortizaciones"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/reportes/pagos/amortizaciones/editar.html'
    form_class = forms.AmortizacionesUpdate
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        pago = models.Pagos.objects.get(id=self.kwargs['pk_pago'])
        amortizacion = models.Amortizaciones.objects.get(id=self.kwargs['pk_amortizacion'])

        if not amortizacion.disabled and amortizacion.estado == 'Pendiente':
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('../../')

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_pago': self.kwargs['pk_pago'],
            'pk_amortizacion': self.kwargs['pk_amortizacion']
        }

    def form_valid(self, form):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        pago = models.Pagos.objects.get(id=self.kwargs['pk_pago'])
        amortizacion = models.Amortizaciones.objects.get(id=self.kwargs['pk_amortizacion'])

        valor_inicial = float(amortizacion.valor.amount)
        valor = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))

        try:
            siguiente_amortizacion = models.Amortizaciones.objects.get(pago = pago, consecutivo = amortizacion.consecutivo+1)
        except:
            models.Amortizaciones.objects.create(
                pago = pago,
                valor = valor_inicial - valor,
                estado = 'Pendiente',
                consecutivo = amortizacion.consecutivo+1
            )
            amortizacion.valor = valor
            amortizacion.save()
            pago.cuotas += 1
            pago.save()
        else:
            valor_siguiente_amortizacion = float(siguiente_amortizacion.valor.amount)
            siguiente_amortizacion.valor = valor_siguiente_amortizacion + valor_inicial - valor
            siguiente_amortizacion.save()
            amortizacion.valor = valor
            amortizacion.save()
            pago.cuotas += 1
            pago.save()

        return super(AmortizacionesPagosUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        reporte = models.Reportes.objects.get(id=self.kwargs['pk'])
        pago = models.Pagos.objects.get(id=self.kwargs['pk_pago'])
        amortizacion = models.Amortizaciones.objects.get(id=self.kwargs['pk_amortizacion'])
        kwargs['title'] = "Editar amortización"
        kwargs['breadcrum_1'] = reporte.nombre
        kwargs['breadcrum_2'] = pago.tercero.get_full_name()
        kwargs['breadcrum_active'] = amortizacion.consecutivo
        return super(AmortizacionesPagosUpdateView,self).get_context_data(**kwargs)
#----------------------------------------------------------------------------------

#-------------------------------------- PAGOS -------------------------------------

class ConsultaPagosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.direccion_financiera.consulta_pagos.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/consulta_pagos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "consulta de pagos"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/consulta_pagos/'
        return super(ConsultaPagosListView,self).get_context_data(**kwargs)


class ConsultaPagosTerceroListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.direccion_financiera.consulta_pagos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/consulta_pagos/tercero/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "PAGOS DE TERCEROS"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/terceros/pagos/' + str(self.kwargs['pk'])
        kwargs['breadcrum_active'] = rh_models.Contratistas.objects.get(pk = kwargs['pk']).fullname()
        kwargs['consulta_dinamica'] = models.Pagos.objects.filter(tercero_id=self.kwargs['pk']).count() > 0
        return super(ConsultaPagosTerceroListView,self).get_context_data(**kwargs)


class ConsultaPagosTerceroDinamicaListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        TemplateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.consulta_pagos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/consulta_pagos/tercero/consulta_dinamica.html'

    def get_context_data(self, **kwargs):
        contratista = rh_models.Contratistas.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "CONSULTA DINAMICA DE PAGOS"
        kwargs['breadcrum_active'] = contratista.fullname()
        kwargs['pk_str'] = self.kwargs['pk']
        kwargs['years'] = json.dumps(contratista.get_years_pagos())
        return super(ConsultaPagosTerceroDinamicaListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#---------------------------------- DESPLAZAMIENTOS -------------------------------

class SolicitudesDesplazamientoListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/solicitudes_desplazamiento/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOLICITUDES DE DESPLAZAMIENTO"
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/solicitudes_desplazamiento/'
        return super(SolicitudesDesplazamientoListView,self).get_context_data(**kwargs)



class UpdateEstadoSolicitudView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.financiera",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/solicitudes_desplazamiento/financiera.html'
    form_class = FinancieraSolicitudForm
    success_url = "../../"
    model = Solicitudes


    def form_valid(self, form):
        self.object = form.save()
        self.object.actualizacion = timezone.now()
        self.object.save()
        return super(UpdateEstadoSolicitudView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        solicitud = Solicitudes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "APROBACIÓN DE LA SOLICITUD"
        kwargs['breadcrum_active'] = solicitud.nombre
        return super(UpdateEstadoSolicitudView,self).get_context_data(**kwargs)



class ListaDesplazamientosView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver"

        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/solicitudes_desplazamiento/lista_desplazamientos.html'


    def get_context_data(self, **kwargs):
        solicitud = Solicitudes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "DESPLAZAMIENTOS"
        kwargs['breadcrum_active'] = solicitud.nombre
        kwargs['url_datatable'] = '/rest/v1.0/direccion_financiera/solicitudes_desplazamiento/desplazamientos/{0}'.format(self.kwargs['pk'])
        kwargs['permiso_aprobar'] = self.request.user.has_perm('usuarios.direccion_financiera.solicitudes_desplazamiento.aprobar') and solicitud.file2 == ''
        return super(ListaDesplazamientosView,self).get_context_data(**kwargs)


class DesplazamientosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'direccion_financiera/solicitudes_desplazamiento/editar.html'
    form_class = forms.DesplazamientoFinancieraForm
    success_url = "../../"
    model = Desplazamiento
    pk_url_kwarg = 'pk_desplazamiento'


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.valor = float(form.cleaned_data['valor'].replace('$ ','').replace(',',''))
        if self.object.verificado:
            self.object.estado = 'Verificado'
        else:
            self.object.estado = None
        self.object.save()
        return super(DesplazamientosUpdateView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        solicitud = Solicitudes.objects.get(id=self.kwargs['pk'])
        desplazamiento = Desplazamiento.objects.get(id=self.kwargs['pk_desplazamiento'])
        kwargs['title'] = "EDITAR DESPLAZAMIENTO"
        kwargs['breadcrum_active'] = solicitud.nombre
        kwargs['breadcrum_active_1'] = desplazamiento.get_name()
        return super(DesplazamientosUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_desplazamiento': self.kwargs['pk_desplazamiento']
        }


class DesplazamientosDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.eliminar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        solicitud = Solicitudes.objects.get(id = self.kwargs['pk'])
        desplazamiento = Desplazamiento.objects.get(id = self.kwargs['pk_desplazamiento'])

        desplazamiento.delete()

        return HttpResponseRedirect('../../')


class DesplazamientosAprobarView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        solicitud = Solicitudes.objects.get(id=self.kwargs['pk'])
        desplazamientos = Desplazamiento.objects.filter(solicitud = solicitud)

        if solicitud.file2 == '':
            desplazamientos.update(estado = 'Aprobado')
            solicitud.estado = 'Aprobado'
            solicitud.actualizacion = timezone.now()
            solicitud.save()

        functions.build_desplazamiento_file(self.kwargs['pk'])
        return HttpResponseRedirect('../../../')

class DesplazamientosRechazarView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
            "usuarios.direccion_financiera.solicitudes_desplazamiento.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        solicitud = Solicitudes.objects.get(id=self.kwargs['pk'])
        desplazamientos = Desplazamiento.objects.filter(solicitud = solicitud)

        if solicitud.file2 == '':
            desplazamientos.update(estado = 'Rechazado')
            solicitud.estado = 'Rechazado'
            solicitud.file = None
            solicitud.actualizacion = timezone.now()
            solicitud.save()

        return HttpResponseRedirect('../../../')

#----------------------------------------------------------------------------------