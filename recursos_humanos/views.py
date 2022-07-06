from django.contrib.messages import get_messages
from django.db.models import Sum
from django.views.generic import TemplateView, CreateView, UpdateView, View, FormView
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import forms, models, functions
from django.shortcuts import redirect
import io
from dateutil import relativedelta as rdelta
import calendar
from datetime import date, datetime
import pdfkit
from django.core.files import File
from delta import html
import json
from bs4 import BeautifulSoup
import os
from django.utils import timezone
from PyPDF2 import PdfFileMerger
from recursos_humanos.functions import numero_to_letras
from recursos_humanos.models import Collects_Account, Contratos, Cuts
from recursos_humanos.tasks import send_mail_templated_certificacion
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_DIRECCION_FINANCIERA
import mimetypes
from django.http import HttpResponseRedirect
from recursos_humanos import tasks
from reportes.models import Reportes
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms
from recursos_humanos import utils


# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class RhoptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/lista.html'
    permissions = {
        "all": ["usuarios.recursos_humanos.ver"]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(RhoptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.recursos_humanos.contratistas.ver'):
            items.append({
                'sican_categoria': 'Recursos humanos',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'contratistas/',
                'sican_name': 'Contratistas',
                'sican_icon': 'work',
                'sican_description': 'Registro y actualización de datos personales, contratos y soportes'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.soportes.ver'):
            items.append({
                'sican_categoria': 'Recursos humanos',
                'sican_color': 'orange darken-4',
                'sican_order': 2,
                'sican_url': 'soportes/tipologia/',
                'sican_name': 'Tipologia de soportes',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Caracterización de cada uno de los soportes disponibles en el módulo'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.soportes.ver'):
            items.append({
                'sican_categoria': 'Recursos humanos',
                'sican_color': 'brown darken-4',
                'sican_order': 3,
                'sican_url': 'soportes/grupos/',
                'sican_name': 'Grupo de soportes',
                'sican_icon': 'group_work',
                'sican_description': 'Agrupación de soportes requeridos para la legalización de contrato'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.certificaciones.ver'):
            items.append({
                'sican_categoria': 'Recursos humanos',
                'sican_color': 'yellow darken-4',
                'sican_order': 4,
                'sican_url': 'certificaciones/',
                'sican_name': 'Certificaciones',
                'sican_icon': 'group_work',
                'sican_description': 'Construcción y consolidación de certificaciones emitidas por la entidad'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.hv.ver'):
            items.append({
                'sican_categoria': 'Recursos humanos',
                'sican_color': 'pink darken-4',
                'sican_order': 5,
                'sican_url': 'hv/',
                'sican_name': 'Hojas de vida',
                'sican_icon': 'insert_drive_file',
                'sican_description': 'Hojas de vida del personal para la ejecución del proyecto'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.contratistas.ver'):
            items.append({
                'sican_categoria': 'Contratos',
                'sican_color': 'green darken-4',
                'sican_order': 6,
                'sican_url': 'contratos/',
                'sican_name': 'Contratos',
                'sican_icon': 'add_to_photos',
                'sican_description': 'Listado de contratos suscritos por la asociación'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.cortes.ver'):
            items.append({
                'sican_categoria': 'Cortes de pago',
                'sican_color': 'blue darken-4',
                'sican_order': 7,
                'sican_url': 'cuts/',
                'sican_name': 'Cortes de pago',
                'sican_icon': 'attach_money',
                'sican_description': 'Listado de cortes de pago'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.liquidacion.ver'):
            items.append({
                'sican_categoria': 'Liquidacion',
                'sican_color': '#e53935 red darken-3',
                'sican_order': 8,
                'sican_url': 'liquidations/',
                'sican_name': 'Liquidaciones',
                'sican_icon': 'assignment',
                'sican_description': 'Listado de contratos para liquidacion'
            })

        if self.request.user.has_perm('usuarios.recursos_humanos.cargos.ver'):
            items.append({
                'sican_categoria': 'Cargos',
                'sican_color': 'blue-grey darken-3',
                'sican_order': 9,
                'sican_url': 'cargos/',
                'sican_name': 'Cargos',
                'sican_icon': 'folder',
                'sican_description': 'Listado de cargos'
            })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "recursos humanos"
        kwargs['items'] = self.get_items()
        return super(RhoptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#-------------------------------- CONTRATISTAS ------------------------------------

class ContratistasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.recursos_humanos.contratistas.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "contratistas"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratistas/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.contratistas.crear')
        return super(ContratistasListView,self).get_context_data(**kwargs)


class ContratistasCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratistas.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/crear.html'
    form_class = forms.ContratistaForm
    success_url = "../"
    model = models.Contratistas

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR CONTRATISTA"
        return super(ContratistasCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.usuario_creacion = self.request.user
        self.object.save()
        return super(ContratistasCreateView, self).form_valid(form)


class ContratistasUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratistas.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/editar.html'
    form_class = forms.ContratistaForm
    success_url = "../../"
    model = models.Contratistas


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR CONTRATISTA"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.certificaciones.crear')
        return super(ContratistasUpdateView,self).get_context_data(**kwargs)

class CertificacionesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.certificaciones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/crear_certificacion.html'
    form_class = forms.CertificacionesForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Crear certificación"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id = self.kwargs['pk']).fullname()
        return super(CertificacionesCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        delta_obj = json.loads(form.cleaned_data['contenido'])
        html_render = BeautifulSoup(html.render(delta_obj['ops']),"html.parser",from_encoding='utf-8')



        template_no_header = BeautifulSoup(open(settings.STATICFILES_DIRS[0] + '/pdfkit/certificaciones/no_header/certificacion_direccion_financiera.html',
                                  'rb'), "html.parser")

        template_header = BeautifulSoup(open(settings.STATICFILES_DIRS[0] + '/pdfkit/certificaciones/header/certificacion_direccion_financiera.html',
                                  'rb'), "html.parser")

        template_no_header_tag = template_no_header.find(class_='contenido')
        template_no_header_tag.insert(1,html_render)


        contratista = models.Contratistas.objects.get(id = self.kwargs['pk'])
        certifiacion = models.Certificaciones.objects.create(
            contratista=contratista,
            usuario_creacion=self.request.user,
            usuario_actualizacion=self.request.user,
            delta = form.cleaned_data['contenido'],
            firma = form.cleaned_data['firma']
        )

        template_no_header_tag = template_no_header.find(class_='codigo_span')
        template_no_header_tag.insert(1, str(certifiacion.codigo))



        certifiacion.pdf.save('certificacion.pdf',File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))
        certifiacion.html.save('pdf.html',File(io.BytesIO(template_no_header.prettify(encoding='utf-8'))))

        template_header_tag = template_header.find(class_='contenido')
        template_header_tag.insert(1, html_render)

        template_header_tag = template_header.find(class_='codigo_span')
        template_header_tag.insert(1, str(certifiacion.codigo))

        certifiacion.html_template.save('certificacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))


        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

        if settings.DEBUG:
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            pdfkit.from_file(certifiacion.html.path, certifiacion.pdf.path, {
                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/header/header.html',
                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/footer/footer.html',
                '--enable-local-file-access': None,
                '--page-size': 'Letter'
            }, configuration=config)
        else:
            data = pdfkit.from_url(
                url=certifiacion.html.url,
                output_path=False,
                options={
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }
            )
            certifiacion.pdf.save('certificacion.pdf', File(io.BytesIO(data)))

        if form.cleaned_data['notificar'] == True:
            adjuntos = [
                ('CERTIFICACION.' + str(certifiacion.pdf.name.split('.')[-1]), certifiacion.pdf.read(),
                 mimetypes.guess_type(certifiacion.pdf.name)[0])
            ]

            send_mail_templated_certificacion(
                'mail/recursos_humanos/certificacion.tpl',
                {
                    'url_base': 'https://' + self.request.META['HTTP_HOST'],
                    'nombre': certifiacion.contratista.nombres,
                    'codigo': str(certifiacion.codigo),
                    'link': 'http://uni2data.com/certificaciones/{0}'.format(str(certifiacion.codigo)),
                },
                DEFAULT_FROM_EMAIL,
                [contratista.email, EMAIL_HOST_USER],
                attachments=adjuntos
            )

        return redirect(certifiacion.pdf.url)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}


#----------------------------------------------------------------------------------

#---------------------------------- CONTRATOS -------------------------------------

class ContratosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "contratos"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratistas/contratos/' + str(kwargs['pk'])
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.contratos.crear')
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        return super(ContratosListView,self).get_context_data(**kwargs)


class ContratosEstadoListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "contratos"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratos/'
        return super(ContratosEstadoListView,self).get_context_data(**kwargs)


class ContratosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratos.ver",
            "usuarios.recursos_humanos.contratos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/crear.html'
    form_class = forms.ContratoForm
    form_class_super_user = forms.ContratoFormSuperUser
    success_url = "../"
    model = models.Contratos

    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:

            if self.request.user.is_superuser:
                return self.form_class_super_user
            else:
                return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)



    def get_context_data(self, **kwargs):
        contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "CREAR CONTRATO"
        kwargs['breadcrum_1'] = contratista.fullname()
        kwargs['contratista_nombre'] = contratista.fullname()
        kwargs['contratista_cedula'] = contratista.cedula

        kwargs['minuta_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['liquidacion_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['renuncia_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['otro_si_1_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['otro_si_2_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['otro_si_3_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'

        return super(ContratosCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ','').replace(',',''))
        self.object.transporte = float(form.cleaned_data['transporte_char'].replace('$ ','').replace(',',''))
        self.object.valor_mensual = float(form.cleaned_data['valor_mensual_char'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(ContratosCreateView, self).form_valid(form)


class ContratosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratos.ver",
            "usuarios.recursos_humanos.contratos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/editar.html'
    form_class = forms.ContratoForm
    form_class_super_user = forms.ContratoFormSuperUser
    success_url = "../../"
    model = models.Contratos
    pk_url_kwarg = 'pk_contrato'

    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:

            if self.request.user.is_superuser:
                return self.form_class_super_user
            else:
                return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ','').replace(',',''))
        self.object.transporte = float(form.cleaned_data['transporte_char'].replace('$ ','').replace(',',''))
        self.object.valor_mensual = float(form.cleaned_data['valor_mensual_char'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(ContratosUpdateView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])

        kwargs['title'] = "EDITAR CONTRATO"
        kwargs['breadcrum_1'] = contratista.fullname()
        kwargs['breadcrum_2'] = contrato.nombre
        kwargs['contratista_nombre'] = contratista.fullname()
        kwargs['contratista_cedula'] = contratista.cedula

        kwargs['minuta_url'] = contrato.pretty_print_url_minuta()
        kwargs['liquidacion_url'] = contrato.pretty_print_url_liquidacion()
        kwargs['renuncia_url'] = contrato.pretty_print_url_renuncia()

        kwargs['otro_si_1_url'] = contrato.pretty_print_url_otrosi_1()
        kwargs['otro_si_2_url'] = contrato.pretty_print_url_otrosi_2()
        kwargs['otro_si_3_url'] = contrato.pretty_print_url_otrosi_3()

        return super(ContratosUpdateView,self).get_context_data(**kwargs)


class ContratosEstadoUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratos.ver",
            "usuarios.recursos_humanos.contratos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratos/editar.html'
    form_class = forms.ContratoForm
    success_url = "../../"
    model = models.Contratos
    pk_url_kwarg = 'pk_contrato'


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ','').replace(',',''))
        self.object.transporte = float(form.cleaned_data['transporte_char'].replace('$ ','').replace(',',''))
        self.object.valor_mensual = float(form.cleaned_data['valor_mensual_char'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(ContratosEstadoUpdateView, self).form_valid(form)


    def get_context_data(self, **kwargs):

        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])

        kwargs['title'] = "EDITAR CONTRATO"
        kwargs['breadcrum_1'] = contrato.nombre
        kwargs['contratista_nombre'] = contrato.contratista.fullname()
        kwargs['contratista_cedula'] = contrato.contratista.cedula

        kwargs['minuta_url'] = contrato.pretty_print_url_minuta()
        kwargs['liquidacion_url'] = contrato.pretty_print_url_liquidacion()
        kwargs['renuncia_url'] = contrato.pretty_print_url_renuncia()

        return super(ContratosEstadoUpdateView,self).get_context_data(**kwargs)

#------------------------------ OTROS SI --------------------------------

class ContratosOtrossiListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.otros_si.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/otros_si/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Otros Si"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratistas/contratos/' + str(self.kwargs['pk']) + \
                                  '/otros_si/' + str(self.kwargs['pk_contrato'])

        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.otros_si.crear')
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_contrato']).nombre
        return super(ContratosOtrossiListView,self).get_context_data(**kwargs)



class ContratosOtrossiCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratos.ver",
            "usuarios.recursos_humanos.otros_si.ver",
            "usuarios.recursos_humanos.otros_si.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/otros_si/crear.html'
    form_class = forms.OtrosiForm
    form_class_super_user = forms.OtrosiFormSuperUser
    success_url = "../"
    model = models.Otros_si
    pk_url_kwarg = 'pk_soporte_contrato'

    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:

            if self.request.user.is_superuser:
                return self.form_class_super_user
            else:
                return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)



    def get_context_data(self, **kwargs):
        contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        kwargs['title'] = "CREAR OTRO SI"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_contrato']).nombre
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'

        return super(ContratosOtrossiCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        self.object = form.save(commit=False)
        self.object.contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        self.object.contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ','').replace(',',''))
        self.object.valor_total = float(form.cleaned_data['valor_total_char'].replace('$ ', '').replace(',', ''))
        self.object.fin=form.cleaned_data['fin']
        self.object.fecha_original = contrato.fin
        self.object.save()

        valor_suma=self.object.valor
        valor_contrato=contrato.valor
        Total=valor_suma+valor_contrato
        contrato.valor = Total
        fin_anterior= contrato.fin
        fin_otro_si=self.object.fin


        if  fin_anterior <  fin_otro_si:
            contrato.fin = form.cleaned_data['fin']
        else:
            pass

        contrato.save()


        return super(ContratosOtrossiCreateView, self).form_valid(form)


class ContratosOtrossiUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratistas.ver",
            "usuarios.recursos_humanos.contratos.ver",
            "usuarios.recursos_humanos.otros_si.ver",
            "usuarios.recursos_humanos.otros_si.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/otros_si/editar.html'
    form_class = forms.OtrosiForm
    form_class_super_user = forms.OtrosiFormSuperUser
    success_url = "../../"
    model = models.Otros_si
    pk_url_kwarg = 'pk_otro_si'


    def get_form_class(self):
        """Return the form class to use in this view."""
        if self.fields is not None and self.form_class:
            raise ImproperlyConfigured(
                "Specifying both 'fields' and 'form_class' is not permitted."
            )
        if self.form_class:

            if self.request.user.is_superuser:
                return self.form_class_super_user
            else:
                return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                raise ImproperlyConfigured(
                    "Using ModelFormMixin (base class of %s) without "
                    "the 'fields' attribute is prohibited." % self.__class__.__name__
                )

            return model_forms.modelform_factory(model, fields=self.fields)

    def get_context_data(self, **kwargs):
        contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        otros_si= models.Otros_si.objects.get(id=self.kwargs['pk_otro_si'])
        kwargs['title'] = "EDITAR OTRO SI"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_contrato']).nombre
        kwargs['breadcrum_active_2'] = models.Otros_si.objects.get(id=self.kwargs['pk_otro_si']).nombre
        kwargs['url_file'] = otros_si.pretty_print_url_otro_si()

        return super(ContratosOtrossiUpdateView,self).get_context_data(**kwargs)




    def form_valid(self, form):
        otros_si= models.Otros_si.objects.get(id=self.kwargs['pk_otro_si'])
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        valor_anterior = otros_si.valor

        self.object = form.save(commit=False)
        self.object.contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])
        self.object.contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ', '').replace(',', ''))
        self.object.valor_total = float(form.cleaned_data['valor_total_char'].replace('$ ', '').replace(',', ''))
        self.object.fin = form.cleaned_data['fin']
        self.object.fecha_original = contrato.fin
        self.object.save()



        valor_contrato = contrato.valor
        resta = valor_contrato - valor_anterior
        suma= self.object.valor
        total = resta + suma
        contrato.valor = total
        fin_anterior = contrato.fin

        fin_otro_si = self.object.fin

        if fin_anterior < fin_otro_si:
            contrato.fin = form.cleaned_data['fin']
        else:
            pass
        contrato.save()

        return super(ContratosOtrossiUpdateView, self).form_valid(form)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_contrato': self.kwargs['pk_contrato'],
            'pk_otros_si': self.kwargs['pk_otro_si'],
        }


class ContratosOtrossiDeleteView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.otro_si = models.Otros_si.objects.get(id=self.kwargs['pk_otro_si'])
        self.contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
        self.contratista = models.Contratistas.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.contratistas.ver",
                "usuarios.recursos_humanos.contratos.ver",
                "usuarios.recursos_humanos.otros_si.ver",
                "usuarios.recursos_humanos.otros_si.editar"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['all']):

                otros_si = models.Otros_si.objects.get(id=self.kwargs['pk_otro_si'])
                valor_anterior = otros_si.valor
                contrato = models.Contratos.objects.get(id=self.kwargs['pk_contrato'])
                valor_contrato = contrato.valor
                resta = valor_contrato - valor_anterior
                total = resta
                contrato.valor = total
                contrato.fin = otros_si.fecha_original
                contrato.save()
                self.otro_si.delete()



                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


#----------------------------------------------------------------------------------


#--------------------------------- TIPO SOPORTES ----------------------------------

class SoportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/tipologia_soportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Tipologia de soportes"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/soportes/tipologia/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.soportes.crear')
        return super(SoportesListView,self).get_context_data(**kwargs)


class SoportesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/tipologia_soportes/crear.html'
    form_class = forms.SoporteForm
    success_url = "../"
    model = models.Soportes

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Crear tipo de soporte"
        return super(SoportesCreateView,self).get_context_data(**kwargs)


class SoportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/tipologia_soportes/editar.html'
    form_class = forms.SoporteForm
    success_url = "../../"
    model = models.Soportes



    def get_context_data(self, **kwargs):

        kwargs['title'] = "Editar tipo de soporte"
        kwargs['breadcrum_active'] = models.Soportes.objects.get(id=self.kwargs['pk']).nombre

        return super(SoportesUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#--------------------------------- GRUPO SOPORTES ---------------------------------

class GruposSoportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/grupo_soportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Grupo de soportes"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/soportes/grupos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.soportes.crear')
        return super(GruposSoportesListView,self).get_context_data(**kwargs)


class GruposSoportesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/grupo_soportes/crear.html'
    form_class = forms.GruposSoportesForm
    success_url = "../"
    model = models.GruposSoportes

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Crear grupo de soportes"
        return super(GruposSoportesCreateView,self).get_context_data(**kwargs)


class GruposSoportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/grupo_soportes/editar.html'
    form_class = forms.GruposSoportesForm
    success_url = "../../"
    model = models.GruposSoportes



    def get_context_data(self, **kwargs):

        kwargs['title'] = "Editar grupo de soportes"
        kwargs['breadcrum_active'] = models.GruposSoportes.objects.get(id=self.kwargs['pk']).nombre

        return super(GruposSoportesUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------ SOPORTES CONTRATOS --------------------------------

class ContratosSoportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/soportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Soportes de contrato"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratistas/contratos/' + str(self.kwargs['pk']) + \
                                  '/soportes/' + str(self.kwargs['pk_soporte'])

        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.soportes.crear')
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_soporte']).nombre
        return super(ContratosSoportesListView,self).get_context_data(**kwargs)


class ContratosEstadoSoportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratos/soportes/lista.html'


    def get_context_data(self, **kwargs):

        contrato = models.Contratos.objects.get(id=self.kwargs['pk_soporte'])

        kwargs['title'] = "Soportes de contrato"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/contratistas/contratos/' + str(contrato.contratista.id) + \
                                  '/soportes/' + str(self.kwargs['pk_soporte'])


        kwargs['breadcrum_active_1'] = contrato.nombre
        return super(ContratosEstadoSoportesListView,self).get_context_data(**kwargs)


class ContratosSoportesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/soportes/crear.html'
    form_class = forms.SoportesContratosCreateForm
    success_url = "../"
    model = models.SoportesContratos

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Nuevo soporte de contrato"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_soporte']).nombre
        return super(ContratosSoportesCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.contrato = models.Contratos.objects.get(id = self.kwargs['pk_soporte'])
        self.object.save()
        return super(ContratosSoportesCreateView, self).form_valid(form)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_soporte': self.kwargs['pk_soporte'],
        }


class ContratosSoportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratistas/contratos/soportes/editar.html'
    form_class = forms.SoportesContratosForm
    success_url = "../../"
    model = models.SoportesContratos
    pk_url_kwarg = 'pk_soporte_contrato'



    def get_context_data(self, **kwargs):
        soporte = models.SoportesContratos.objects.get(id = self.kwargs['pk_soporte_contrato'])
        kwargs['title'] = "Editar soporte de contrato"
        kwargs['breadcrum_active'] = models.Contratistas.objects.get(id=self.kwargs['pk']).fullname()
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_soporte']).nombre
        kwargs['breadcrum_active_2'] = soporte.soporte.nombre
        kwargs['soporte_url'] = soporte.pretty_print_url_file()
        kwargs['nombre_soporte'] = str(soporte.soporte)

        return super(ContratosSoportesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_soporte': self.kwargs['pk_soporte'],
        }


class ContratosEstadoSoportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.soportes.ver",
            "usuarios.recursos_humanos.soportes.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/contratos/soportes/editar.html'
    form_class = forms.SoportesContratosForm
    success_url = "../../"
    model = models.SoportesContratos
    pk_url_kwarg = 'pk_soporte_contrato'



    def get_context_data(self, **kwargs):
        soporte = models.SoportesContratos.objects.get(id = self.kwargs['pk_soporte_contrato'])
        kwargs['title'] = "Editar soporte de contrato"
        kwargs['breadcrum_active_1'] = models.Contratos.objects.get(id=self.kwargs['pk_soporte']).nombre
        kwargs['breadcrum_active_2'] = soporte.soporte.nombre
        kwargs['soporte_url'] = soporte.pretty_print_url_file()
        kwargs['nombre_soporte'] = str(soporte.soporte)

        return super(ContratosEstadoSoportesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_soporte'])
        return {
            'pk': contrato.contratista.id,
            'pk_soporte': self.kwargs['pk_soporte'],
        }

#----------------------------------------------------------------------------------
#-------------------------------- CERTIFICACIONES ---------------------------------

class CertificacionesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.certificaciones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/certificaciones/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CERTIFICACIONES"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/certificaciones/'
        return super(CertificacionesListView,self).get_context_data(**kwargs)


class CertificacionesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.certificaciones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/certificaciones/editar.html'
    form_class = forms.CertificacionesUpdateForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Actualizar certificación"
        kwargs['breadcrum_active'] = models.Certificaciones.objects.get(id = self.kwargs['pk']).contratista.fullname()
        return super(CertificacionesUpdateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        delta_obj = json.loads(form.cleaned_data['contenido'])
        html_render = BeautifulSoup(html.render(delta_obj['ops']),"html.parser",from_encoding='utf-8')

        template_no_header = BeautifulSoup(open(
            settings.STATICFILES_DIRS[0] + '/pdfkit/certificaciones/no_header/certificacion_direccion_financiera.html',
            'rb'), "html.parser")

        template_header = BeautifulSoup(open(
            settings.STATICFILES_DIRS[0] + '/pdfkit/certificaciones/header/certificacion_direccion_financiera.html',
            'rb'), "html.parser")


        template_no_header_tag = template_no_header.find(class_='contenido')
        template_no_header_tag.insert(1,html_render)



        certifiacion = models.Certificaciones.objects.get(id = self.kwargs['pk'])
        certifiacion.firma = form.cleaned_data['firma']
        certifiacion.delta = form.cleaned_data['contenido']
        certifiacion.save()
        contratista = certifiacion.contratista

        template_no_header_tag = template_no_header.find(class_='codigo_span')
        template_no_header_tag.insert(1, str(certifiacion.codigo))



        certifiacion.pdf.save('certificacion.pdf',File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))
        certifiacion.html.save('pdf.html',File(io.BytesIO(template_no_header.prettify(encoding='utf-8'))))

        template_header_tag = template_header.find(class_='contenido')
        template_header_tag.insert(1, html_render)

        template_header_tag = template_header.find(class_='codigo_span')
        template_header_tag.insert(1, str(certifiacion.codigo))

        certifiacion.html_template.save('certificacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))


        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if settings.DEBUG:
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            pdfkit.from_file(certifiacion.html.path, certifiacion.pdf.path, {
                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/header/header.html',
                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/footer/footer.html',
                '--enable-local-file-access': None,
                '--page-size': 'Letter'
            },configuration=config)
        else:
            data = pdfkit.from_url(
                url=certifiacion.html.url,
                output_path=False,
                options={
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }
            )
            certifiacion.pdf.save('certificacion.pdf', File(io.BytesIO(data)))

        if form.cleaned_data['notificar'] == True:
            adjuntos = [
                ('CERTIFICACION.' + str(certifiacion.pdf.name.split('.')[-1]), certifiacion.pdf.read(),
                 mimetypes.guess_type(certifiacion.pdf.name)[0])
            ]

            send_mail_templated_certificacion(
                'mail/recursos_humanos/certificacion.tpl',
                {
                    'url_base': 'https://' + self.request.META['HTTP_HOST'],
                    'nombre': certifiacion.contratista.nombres,
                    'codigo': str(certifiacion.codigo),
                    'link': 'https://sican.asoandes.org/certificaciones/{0}'.format(str(certifiacion.codigo)),
                },
                DEFAULT_FROM_EMAIL,
                [contratista.email, EMAIL_HOST_USER],
                attachments=adjuntos
            )

        return redirect(certifiacion.pdf.url)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class CertificacionesSearchView(FormView):
    """
    """
    template_name = 'no_auth/search.html'
    form_class = forms.CertificacionesSearchForm

    def get_context_data(self, **kwargs):
        kwargs['url_consulta'] = '/rest/v1.0/recursos_humanos/certificaciones/cedula/'
        return super(CertificacionesSearchView, self).get_context_data(**kwargs)


class CertificacionesPkView(TemplateView):
    """
    """

    def get_template_names(self):
        certificacion = models.Certificaciones.objects.get(codigo = self.kwargs['pk'])
        return ['/'.join(['Certificaciones',str(self.kwargs['pk']),os.path.basename(certificacion.html_template.file.name)])]
#----------------------------------------------------------------------------------
#------------------------------------- HV -----------------------------------------

class HvListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.hv.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/hv/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "HOJAS DE VIDA"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/hv/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.hv.crear')
        return super(HvListView,self).get_context_data(**kwargs)


class HvCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.hv.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/hv/crear.html'
    form_class = forms.HvForm
    success_url = "../"

    def form_valid(self, form):
        self.object = form.save()

        hv = self.object
        models.TrazabilidadHv.objects.create(
            hv=hv,
            usuario_creacion=self.request.user,
            observacion='Creación de la hoja de vida, contratista: {0} - cargo: {1} - envio: Envio {2}'.format(
                str(hv.contratista),
                hv.cargo,
                hv.envio
            )
        )
        return super(HvCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA HOJA DE VIDA"
        kwargs['url_contratistas'] = '/rest/v1.0/recursos_humanos/hv/autocomplete/contratistas/'
        kwargs['file_url'] = ' N/A'
        return super(HvCreateView,self).get_context_data(**kwargs)



class HvUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.hv.ver",
            "usuarios.recursos_humanos.hv.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/hv/editar.html'
    form_class = forms.HvForm
    model = models.Hv
    success_url = "../../"

    def form_valid(self, form):
        self.object = form.save()

        hv = self.object
        models.TrazabilidadHv.objects.create(
            hv=hv,
            usuario_creacion=self.request.user,
            observacion='Actualización de la hoja de vida, contratista: {0} - cargo: {1} - envio: Envio {2}'.format(
                str(hv.contratista),
                hv.cargo,
                hv.envio
            )
        )
        return super(HvUpdateView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        hv = models.Hv.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTUALIZAR HOJA DE VIDA"
        kwargs['breadcrum_active'] = hv.contratista.get_full_name()
        kwargs['url_contratistas'] = '/rest/v1.0/recursos_humanos/hv/autocomplete/contratistas/'
        kwargs['file_url'] = hv.pretty_print_url_file()
        return super(HvUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class HvEstadoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.hv.ver",
            "usuarios.recursos_humanos.hv_cpe.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/hv/estado.html'
    form_class = forms.HvEstado
    success_url = "../../"
    model = models.Hv

    def form_valid(self, form):

        self.object = form.save()
        hv = self.object

        trazabilidad = models.TrazabilidadHv.objects.create(
            hv=hv,
            usuario_creacion=self.request.user,
            observacion='Actualización del estado de la hoja de vida, estado: {0}'.format(
                hv.estado
            )
        )
        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        hv = models.Hv.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTUALIZAR ESTADO HOJA DE VIDA"
        kwargs['breadcrum_active'] = hv.contratista.get_full_name()
        kwargs['file_url'] = hv.url_file()
        kwargs['hv'] = hv
        kwargs['url_hv_trazabilidad'] = '/rest/v1.0/recursos_humanos/hv/trazabilidad/{0}/'.format(str(self.kwargs['pk']))
        return super(HvEstadoView,self).get_context_data(**kwargs)


class ContratosReporteListadoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.contratos.ver",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Listado de contratos suscritos y estado de legalización',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_listado_contratos.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')

class HvReporteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.hv.ver",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Estado de aprobación y carga de hojas de vida',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_reporte_hv.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')

#----------------------------------------------------------------------------------

#--------------------------------Cortes--------------------------------------------


class CutsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver"
        ],
        "crear": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver",
            "usuarios.recursos_humanos.cortes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CORTES"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/cuts/'
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear'])
        return super(CutsListView,self).get_context_data(**kwargs)

class CutsCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/add.html'
    form_class = forms.CutsCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
                "usuarios.recursos_humanos.cortes.crear"
            ]
        }
        return permissions

    def form_valid(self, form):

        cut = models.Cuts.objects.create(
            consecutive = models.Cuts.objects.all().count() + 1,
            user_creation = self.request.user,
            name = form.cleaned_data['name'],
            month = form.cleaned_data['month'],
            year = form.cleaned_data['year'],
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CORTE DE PAGO"
        return super(CutsCreateView,self).get_context_data(**kwargs)

class CutsCollectsAddAccountView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/collects/add.html'
    form_class = forms.CutsAddForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
                "usuarios.recursos_humanos.cortes.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        import datetime
        cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        year = int(cut.year)
        month = int(cut.month)
        days_monht = functions.obtener_dias_del_mes(month, year)
        t_init = datetime.date(year, month, 1)
        t_end = datetime.date(year,month,days_monht)

        collects_ids = models.Collects_Account.objects.filter(year=year, month=month).values_list('contract__id',flat=True)
        contracts_ids = Contratos.objects.filter(ejecucion = True, suscrito=True,liquidado = False, fin__gte=t_init).exclude(id__in=collects_ids).values_list('id',flat=True).distinct()

        user = self.request.user

        for contract_id in contracts_ids:
            contract = models.Contratos.objects.get(id=contract_id)
            if form.cleaned_data['contrato_{0}'.format(contract.id)]:
                if float(contract.valor_mensual) <= 0 or float(contract.valor)==None:
                    month_cut = cut.month
                    year_cut = cut.year
                    value = contract.valor
                    start = contract.inicio
                    end = contract.fin
                    rd = rdelta.relativedelta(end,start)

                    rd_months = rd.months
                    rd_days = rd.days
                    days_total = rd_months * 30 + rd_days
                    value_f = float(value)
                    value_total = int(value_f)




                    collects_accounts = models.Collects_Account.objects.filter(contract=contract)
                    total_value_fees = collects_accounts.aggregate(Sum('value_fees'))['value_fees__sum']
                    values_total = round((value_total/days_total) * 30)

                    if total_value_fees == None:
                        total_value_fees_sum =  float(0)
                    else:
                        total_value_fees_sum = float(total_value_fees)

                    if contract.inicio.year == int(year_cut) and contract.inicio.month == int(month_cut):
                        days_monht = functions.obtener_dias_del_mes(month,year)
                        if days_monht == 31:
                            date_rest = date(int(year_cut), int(month_cut), 30)
                            days_rest = date_rest - contract.inicio
                            values_total = (values_total / 30) * (days_rest.days +1)
                        elif days_monht == 30:
                            date_rest = date(int(year_cut), int(month_cut), 30)
                            days_rest = date_rest - contract.inicio
                            values_total = (values_total / 30) * (days_rest.days +1)
                        elif days_monht == 29:
                            date_rest = date(int(year_cut), int(month_cut), 29)
                            days_rest = date_rest - contract.inicio
                            values_total = (values_total / 30) * (days_rest.days + 2)
                        elif days_monht == 28:
                            date_rest = date(int(year_cut), int(month_cut), 28)
                            days_rest = date_rest - contract.inicio
                            values_total = (values_total / 30) * (days_rest.days + 3)

                    if contract.fin.year == int(year_cut) and contract.fin.month == int(month_cut):
                        days_monht = functions.obtener_dias_del_mes(month,year)
                        if contract.fin.day == 30:
                            date_rest = date(int(year_cut), int(month_cut), 1)
                            days_rest = contract.fin - date_rest
                            values_total = (values_total / 30) * (days_rest.days + 1)
                        else:
                            if days_monht == 31:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (values_total / 30) * (days_rest.days)
                            elif days_monht == 30:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (values_total / 30) * (days_rest.days+1)
                            elif days_monht == 29:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (values_total / 30) * (days_rest.days+2)
                            elif days_monht == 28:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (values_total / 30) * (days_rest.days+3)


                    if total_value_fees_sum < value_total:
                        collect_account = models.Collects_Account.objects.create(
                            contract=contract,
                            cut=cut,
                            user_creation=user,
                            estate='Creado',
                            value_fees=values_total,
                            month=cut.month,
                            year=cut.year,
                        )

                        fecha = timezone.now()

                        collect_count = models.Collects_Account.objects.filter(contract=contract).count()
                        collect_count = collect_count

                        collect_account.estate = "Generado"
                        collect_account.estate_inform = "Generado"
                        collect_account.estate_report = "Generado"
                        collect_account.save()
                        month = int(collect_account.month) - 1
                        month = functions.month_converter(month)

                        fee_account_value = collect_account.get_value_fees()
                        fee_value = fee_account_value.replace('$', '').replace(',', '')

                        collect_account.file.delete()
                        collect_account.html.delete()

                        value_money = float(collect_account.value_fees)
                        value_letter_num = value_money
                        value_letter = numero_to_letras(int(value_letter_num))

                        if collect_account.estate != 'Cargado':
                            collect_account.estate = 'Generado'
                        collect_account.save()

                        template_header = BeautifulSoup(
                            open(settings.STATICFILES_DIRS[0]  + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'), "html.parser")

                        template_header_tag = template_header.find(class_='fecha_span')
                        template_header_tag.insert(1, collect_account.pretty_creation_datetime())

                        template_header_tag = template_header.find(class_='number_span')
                        template_header_tag.insert(1, str(collect_count))

                        template_header_tag = template_header.find(class_='contract_span')
                        template_header_tag.insert(1, collect_account.contract.nombre)

                        template_header_tag = template_header.find(class_='contractor_name_span')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_span')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='contractor_name_firm')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_firm')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='value_letter_span')
                        template_header_tag.insert(1, value_letter)

                        template_header_tag = template_header.find(class_='value_letter_num_span')
                        template_header_tag.insert(1, str(value_letter_num))

                        template_header_tag = template_header.find(class_='position_span')
                        template_header_tag.insert(1, str(collect_account.contract.cargo.nombre))


                        template_header_tag = template_header.find(class_='month_span')
                        template_header_tag.insert(1, str(month))

                        template_header_tag = template_header.find(class_='year_span')
                        template_header_tag.insert(1, str(collect_account.year))

                        collect_account.html.save('cuenta_cobro.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

                        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


                        collect_account.file.save('cuenta_cobro.pdf',
                                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))


                        if settings.DEBUG:
                            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                            pdfkit.from_file([collect_account.html.path], collect_account.file.path, {
                                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                '--enable-local-file-access': None,
                                '--page-size': 'Letter'
                            }, configuration=config)
                        else:
                            data = pdfkit.from_url(
                                url=collect_account.html.url,
                                output_path=False,
                                options={
                                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                    '--enable-local-file-access': None,
                                    '--page-size': 'Letter'
                                }
                            )
                            collect_account.file.save('certificacion.pdf', File(io.BytesIO(data)))

                            user = collect_account.contract.get_user_or_none()

                            #if user != None:
                            #    tasks.send_mail_templated_cuenta_cobro(
                            #        'mail/recursos_humanos/cuenta_cobro.tpl',
                            #        {
                            #            'url_base': 'https://' + self.request.META['HTTP_HOST'],
                            #            'Contrato': collect_account.contract.nombre,
                            #            'nombre': collect_account.contract.contratista.nombres,
                            #            'valor': '$ {:20,.2f}'.format(collect_account.value_fees.amount),
                            #        },
                            #        DEFAULT_FROM_EMAIL,
                            #        [user.email, EMAIL_HOST_USER]
                            #    )

                    else:
                        value_rest = int(value_total) - int(total_value_fees)
                        collect_account = models.Collects_Account.objects.create(
                            contract=contract,
                            cut=cut,
                            user_creation=user,
                            estate='Creado',
                            value_fees=value_rest,
                            month=cut.month,
                            year=cut.year,
                        )

                        fecha = timezone.now()

                        collect_count = models.Collects_Account.objects.filter(contract=contract).count()
                        collect_count = collect_count

                        collect_account.estate = "Generado"
                        collect_account.estate_inform = "Generado"
                        collect_account.estate_report = "Generado"
                        collect_account.save()
                        month = int(collect_account.month) - 1
                        month = functions.month_converter(month)

                        fee_account_value = collect_account.get_value_fees()
                        fee_value = fee_account_value.replace('$', '').replace(',', '')

                        collect_account.file.delete()
                        collect_account.html.delete()

                        value_money = float(collect_account.value_fees)
                        value_letter_num = value_money
                        value_letter = numero_to_letras(int(value_letter_num))

                        if collect_account.estate != 'Cargado':
                            collect_account.estate = 'Generado'
                        collect_account.save()

                        template_header = BeautifulSoup(
                            open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'),
                            "html.parser")



                        template_header_tag = template_header.find(class_='fecha_span')
                        template_header_tag.insert(1, collect_account.pretty_creation_datetime())

                        template_header_tag = template_header.find(class_='number_span')
                        template_header_tag.insert(1, str(collect_count))

                        template_header_tag = template_header.find(class_='contract_span')
                        template_header_tag.insert(1, collect_account.contract.nombre)

                        template_header_tag = template_header.find(class_='contractor_name_span')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_span')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='contractor_name_firm')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_firm')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='value_letter_span')
                        template_header_tag.insert(1, value_letter)

                        template_header_tag = template_header.find(class_='value_letter_num_span')
                        template_header_tag.insert(1, str(value_letter_num))

                        template_header_tag = template_header.find(class_='position_span')
                        template_header_tag.insert(1, str(collect_account.contract.cargo.nombre))

                        template_header_tag = template_header.find(class_='month_span')
                        template_header_tag.insert(1, str(month))

                        template_header_tag = template_header.find(class_='year_span')
                        template_header_tag.insert(1, str(collect_account.year))

                        collect_account.html.save('cuenta_cobro.html',
                                                  File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

                        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

                        collect_account.file.save('cuenta_cobro.pdf',
                                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

                        if settings.DEBUG:
                            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                            pdfkit.from_file([collect_account.html.path], collect_account.file.path, {
                                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                '--enable-local-file-access': None,
                                '--page-size': 'Letter'
                            }, configuration=config)
                        else:
                            data = pdfkit.from_url(
                                url=collect_account.html.url,
                                output_path=False,
                                options={
                                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                    '--enable-local-file-access': None,
                                    '--page-size': 'Letter'
                                }
                            )
                            collect_account.file.save('cuenta_cobro.pdf', File(io.BytesIO(data)))
                else:
                    month_cut = cut.month
                    year_cut = cut.year
                    value = contract.valor
                    start = contract.inicio
                    end = contract.fin
                    valor_mensual= contract.valor_mensual



                    collects_accounts = models.Collects_Account.objects.filter(contract=contract)
                    total_value_fees = collects_accounts.aggregate(Sum('value_fees'))['value_fees__sum']


                    if total_value_fees == None:
                        total_value_fees_sum = float(0)
                    else:
                        total_value_fees_sum = float(total_value_fees)

                    if contract.inicio.year == int(year_cut) and contract.inicio.month == int(month_cut):
                        days_monht = functions.obtener_dias_del_mes(month, year)
                        if days_monht == 31:
                            date_rest = date(int(year_cut), int(month_cut), 31)
                            days_rest = date_rest - contract.inicio
                            values_total = (valor_mensual / 30) * (days_rest.days)
                        elif days_monht == 30:
                            date_rest = date(int(year_cut), int(month_cut), 30)
                            days_rest = date_rest - contract.inicio
                            values_total = (valor_mensual / 30) * (days_rest.days+1)
                        elif days_monht == 29:
                            date_rest = date(int(year_cut), int(month_cut), 29)
                            days_rest = date_rest - contract.inicio
                            values_total = (valor_mensual / 30) * (days_rest.days+2)
                        elif days_monht == 28:
                            date_rest = date(int(year_cut), int(month_cut), 28)
                            days_rest = date_rest - contract.inicio
                            values_total = (valor_mensual / 30) * (days_rest.days+3)

                    elif contract.fin.year == int(year_cut) and contract.fin.month == int(month_cut):
                        if contract.fin.day == 30:
                            date_rest = date(int(year_cut), int(month_cut), 1)
                            days_rest = contract.fin - date_rest
                            values_total = (valor_mensual / 30) * (days_rest.days+1)
                        else:
                            days_monht = functions.obtener_dias_del_mes(month, year)
                            if days_monht == 31:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (valor_mensual / 30) * (days_rest.days)
                            elif days_monht == 30:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (valor_mensual / 30) * (days_rest.days+1)
                            elif days_monht == 29:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (valor_mensual / 30) * (days_rest.days + 2)
                            elif days_monht == 28:
                                date_rest = date(int(year_cut), int(month_cut), 1)
                                days_rest = contract.fin - date_rest
                                values_total = (valor_mensual / 30) * (days_rest.days + 3)
                    else:
                        values_total=valor_mensual

                    total_value_fees_sum = total_value_fees_sum + float(values_total)

                    if float(total_value_fees_sum) <= float(value):
                        collect_account = models.Collects_Account.objects.create(
                            contract=contract,
                            cut=cut,
                            user_creation=user,
                            estate='Creado',
                            value_fees=values_total,
                            month=cut.month,
                            year=cut.year,
                        )


                        fecha = timezone.now()

                        collect_count = models.Collects_Account.objects.filter(contract=contract).count()
                        collect_count = collect_count

                        collect_account.estate = "Generado"
                        collect_account.estate_inform = "Generado"
                        collect_account.estate_report = "Generado"
                        collect_account.save()
                        month = int(collect_account.month) - 1
                        month = functions.month_converter(month)

                        fee_account_value = collect_account.get_value_fees()
                        fee_value = fee_account_value.replace('$', '').replace(',', '')

                        collect_account.file.delete()
                        collect_account.html.delete()

                        value_money = float(collect_account.value_fees)
                        value_letter_num = value_money
                        value_letter = numero_to_letras(int(value_letter_num))

                        if collect_account.estate != 'Cargado':
                            collect_account.estate = 'Generado'
                        collect_account.save()

                        template_header = BeautifulSoup(
                            open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'),
                            "html.parser")

                        template_header_tag = template_header.find(class_='fecha_span')
                        template_header_tag.insert(1, collect_account.pretty_creation_datetime())

                        template_header_tag = template_header.find(class_='number_span')
                        template_header_tag.insert(1, str(collect_count))

                        template_header_tag = template_header.find(class_='contract_span')
                        template_header_tag.insert(1, collect_account.contract.nombre)

                        template_header_tag = template_header.find(class_='contractor_name_span')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_span')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='contractor_name_firm')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_firm')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='value_letter_span')
                        template_header_tag.insert(1, value_letter)

                        template_header_tag = template_header.find(class_='value_letter_num_span')
                        template_header_tag.insert(1, str(value_letter_num))

                        template_header_tag = template_header.find(class_='position_span')
                        template_header_tag.insert(1, str(collect_account.contract.cargo.nombre))

                        template_header_tag = template_header.find(class_='month_span')
                        template_header_tag.insert(1, str(month))

                        template_header_tag = template_header.find(class_='year_span')
                        template_header_tag.insert(1, str(collect_account.year))

                        collect_account.html.save('cuenta_cobro.html',
                                                  File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

                        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

                        collect_account.file.save('cuenta_cobro.pdf',
                                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf',
                                                            'rb')))

                        if settings.DEBUG:
                            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                            pdfkit.from_file([collect_account.html.path], collect_account.file.path, {
                                '--header-html': settings.STATICFILES_DIRS[
                                                     0] + '/pdfkit/cuentas_cobro/header/header.html',
                                '--footer-html': settings.STATICFILES_DIRS[
                                                     0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                '--enable-local-file-access': None,
                                '--page-size': 'Letter'
                            }, configuration=config)
                        else:
                            data = pdfkit.from_url(
                                url=collect_account.html.url,
                                output_path=False,
                                options={
                                    '--header-html': settings.STATICFILES_DIRS[
                                                         0] + '/pdfkit/cuentas_cobro/header/header.html',
                                    '--footer-html': settings.STATICFILES_DIRS[
                                                         0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                    '--enable-local-file-access': None,
                                    '--page-size': 'Letter'
                                }
                            )
                            collect_account.file.save('certificacion.pdf', File(io.BytesIO(data)))

                            user = collect_account.contract.get_user_or_none()

                            # if user != None:
                            #    tasks.send_mail_templated_cuenta_cobro(
                            #        'mail/recursos_humanos/cuenta_cobro.tpl',
                            #        {
                            #            'url_base': 'https://' + self.request.META['HTTP_HOST'],
                            #            'Contrato': collect_account.contract.nombre,
                            #            'nombre': collect_account.contract.contratista.nombres,
                            #            'valor': '$ {:20,.2f}'.format(collect_account.value_fees.amount),
                            #        },
                            #        DEFAULT_FROM_EMAIL,
                            #        [user.email, EMAIL_HOST_USER]
                            #    )
                    else:
                        value_rest = float(value) - float(total_value_fees)
                        collect_account = models.Collects_Account.objects.create(
                            contract=contract,
                            cut=cut,
                            user_creation=user,
                            estate='Creado',
                            value_fees=value_rest,
                            month=cut.month,
                            year=cut.year,
                        )

                        fecha = timezone.now()

                        collect_count = models.Collects_Account.objects.filter(contract=contract).count()
                        collect_count = collect_count

                        collect_account.estate = "Generado"
                        collect_account.estate_inform = "Generado"
                        collect_account.estate_report = "Generado"
                        collect_account.save()
                        month = int(collect_account.month) - 1
                        month = functions.month_converter(month)

                        fee_account_value = collect_account.get_value_fees()
                        fee_value = fee_account_value.replace('$', '').replace(',', '')

                        collect_account.file.delete()
                        collect_account.html.delete()

                        value_money = float(collect_account.value_fees)
                        value_letter_num = value_money
                        value_letter = numero_to_letras(int(value_letter_num))

                        if collect_account.estate != 'Cargado':
                            collect_account.estate = 'Generado'
                        collect_account.save()

                        template_header = BeautifulSoup(
                            open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'),
                            "html.parser")

                        template_header_tag = template_header.find(class_='fecha_span')
                        template_header_tag.insert(1, collect_account.pretty_creation_datetime())

                        template_header_tag = template_header.find(class_='number_span')
                        template_header_tag.insert(1, str(collect_count))

                        template_header_tag = template_header.find(class_='contract_span')
                        template_header_tag.insert(1, collect_account.contract.nombre)

                        template_header_tag = template_header.find(class_='contractor_name_span')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_span')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='contractor_name_firm')
                        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

                        template_header_tag = template_header.find(class_='contractor_document_firm')
                        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

                        template_header_tag = template_header.find(class_='value_letter_span')
                        template_header_tag.insert(1, value_letter)

                        template_header_tag = template_header.find(class_='value_letter_num_span')
                        template_header_tag.insert(1, str(value_letter_num))

                        template_header_tag = template_header.find(class_='position_span')
                        template_header_tag.insert(1, str(collect_account.contract.cargo.nombre))

                        template_header_tag = template_header.find(class_='month_span')
                        template_header_tag.insert(1, str(month))

                        template_header_tag = template_header.find(class_='year_span')
                        template_header_tag.insert(1, str(collect_account.year))

                        collect_account.html.save('cuenta_cobro.html',
                                                  File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

                        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

                        collect_account.file.save('cuenta_cobro.pdf',
                                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf',
                                                            'rb')))

                        if settings.DEBUG:
                            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                            pdfkit.from_file([collect_account.html.path], collect_account.file.path, {
                                '--header-html': settings.STATICFILES_DIRS[
                                                     0] + '/pdfkit/cuentas_cobro/header/header.html',
                                '--footer-html': settings.STATICFILES_DIRS[
                                                     0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                '--enable-local-file-access': None,
                                '--page-size': 'Letter'
                            }, configuration=config)
                        else:
                            data = pdfkit.from_url(
                                url=collect_account.html.url,
                                output_path=False,
                                options={
                                    '--header-html': settings.STATICFILES_DIRS[
                                                         0] + '/pdfkit/cuentas_cobro/header/header.html',
                                    '--footer-html': settings.STATICFILES_DIRS[
                                                         0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                                    '--enable-local-file-access': None,
                                    '--page-size': 'Letter'
                                }
                            )
                            collect_account.file.save('cuenta_cobro.pdf', File(io.BytesIO(data)))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        cut=models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        kwargs['title'] = "AGREGAR CUENTA DE COBRO"
        return super(CutsCollectsAddAccountView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_cut': self.kwargs['pk_cut'],
        }


class CutsCollectsAccountView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver",
            "usuarios.recursos_humanos.cuentas_cobro.ver"
        ],
        "crear_cuenta_cobro": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver",
            "usuarios.recursos_humanos.cuentas_cobro.ver",
            "usuarios.recursos_humanos.cuentas_cobro.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/collects/list.html'


    def get_context_data(self, **kwargs):
        cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        kwargs['title'] = "CORTE {0}".format(cut.consecutive)
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/cuts/view/{0}/'.format(cut.id)
        kwargs['breadcrum_active'] = cut.consecutive
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_cuenta_cobro'))
        kwargs['show'] = True if models.Collects_Account.objects.filter(cut=cut).count() == 0 else False
        return super(CutsCollectsAccountView,self).get_context_data(**kwargs)

class CollectAccountUpdateView(FormView):
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/collects/create.html'
    form_class = forms.CollectsAccountForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        self.collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "crear_cuenta_cobro": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
                "usuarios.recursos_humanos.cuentas_cobro.ver",
                "usuarios.recursos_humanos.cuentas_cobro.crear"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('crear_cuenta_cobro')):
                if self.collect_account.estate == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_cuentas_fees(self,collect_account):

        accounts = models.Collects_Account.objects.filter(contract=self.collect_account.contract).exclude(liquidacion=True)
        list= ''
        count= accounts.count()



        for account in accounts:
            month = account.month
            year = account.year
            value = account.value_fees
            cut = account.cut.consecutive


            list += '<p><b>Corte: </b>{0}</p><p><b>Fecha: </b>{1} - {2}</p><ul>{3}</ul>'.format(cut,month,year,value)

        return list



    def form_valid(self, form):
        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        fecha = timezone.now()

        contract = collect_account.contract

        collect_count = models.Collects_Account.objects.filter(contract=contract).count()
        collect_count = collect_count

        collect_account.value_fees = utils.autonumeric2float(form.cleaned_data['value_fees_char'])
        collect_account.estate = "Generado"
        collect_account.save()

        fee_account_value = collect_account.get_value_fees()
        fee_value = fee_account_value.replace('$','').replace(',','')


        collect_account.file.delete()
        collect_account.html.delete()


        value_money= float(collect_account.value_fees)
        value_letter_num = value_money
        value_letter = numero_to_letras(int(value_letter_num))

        month = int(collect_account.month) - 1
        month = functions.month_converter(month)

        if collect_account.estate != 'Cargado':
            collect_account.estate = 'Generado'
        collect_account.save()

        template_header = BeautifulSoup(open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html','rb'), "html.parser")


        template_header_tag = template_header.find(class_='fecha_span')
        template_header_tag.insert(1, collect_account.pretty_creation_datetime())

        template_header_tag = template_header.find(class_='number_span')
        template_header_tag.insert(1, str(collect_count))

        template_header_tag = template_header.find(class_='contract_span')
        template_header_tag.insert(1, collect_account.contract.nombre)

        template_header_tag = template_header.find(class_='contractor_name_span')
        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

        template_header_tag = template_header.find(class_='contractor_document_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

        template_header_tag = template_header.find(class_='contractor_name_firm')
        template_header_tag.insert(1, collect_account.contract.contratista.get_full_name())

        template_header_tag = template_header.find(class_='contractor_document_firm')
        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

        template_header_tag = template_header.find(class_='value_letter_span')
        template_header_tag.insert(1, value_letter)

        template_header_tag = template_header.find(class_='value_letter_num_span')
        template_header_tag.insert(1, str(value_letter_num))

        template_header_tag = template_header.find(class_='position_span')
        template_header_tag.insert(1, str(collect_account.contract.get_cargo()))

        template_header_tag = template_header.find(class_='month_span')
        template_header_tag.insert(1, str(month))

        template_header_tag = template_header.find(class_='year_span')
        template_header_tag.insert(1, str(collect_account.year))

        collect_account.html.save('cuenta_cobro.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

        collect_account.file.save('cuenta_cobro.pdf',
                              File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        if settings.DEBUG:
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            pdfkit.from_file([collect_account.html.path], collect_account.file.path, {
                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                '--enable-local-file-access': None,
                '--page-size': 'Letter'
            }, configuration=config)
        else:
            data = pdfkit.from_url(
                url=collect_account.html.url,
                output_path=False,
                options={
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }
            )
            collect_account.file.save('certificacion.pdf', File(io.BytesIO(data)))

        models.Registration.objects.create(
            cut=collect_account.cut,
            user=self.request.user,
            collect_account = collect_account,
            delta = "Actualizo la cuenta de cobro"
        )

        return super(CollectAccountUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])



        kwargs['title'] = "CUENTA DE COBRO CONTRATO {0}".format(collect_account.contract.nombre)
        kwargs['breadcrum_1'] = cut.consecutive
        kwargs['breadcrum_active'] = collect_account.contract.nombre
        kwargs['value_fees'] = '$ {:20,.2f}'.format(collect_account.value_fees.amount)
        kwargs['value_transport'] = '$ {:20,.2f}'.format(collect_account.value_transport.amount)
        kwargs['corte'] = '{0}'.format(cut.consecutive)
        kwargs['contratista'] = collect_account.contract.contratista.get_full_name()
        kwargs['contrato'] = collect_account.contract.nombre
        kwargs['cuentas_fees'] = self.get_cuentas_fees(collect_account)
        kwargs['inicio'] = collect_account.contract.inicio
        kwargs['fin'] = collect_account.contract.fin
        kwargs['valor'] = collect_account.contract.valor

        return super(CollectAccountUpdateView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_cut': self.kwargs['pk_cut'],
            'pk_collect_account': self.kwargs['pk_collect_account']
        }

class CollectAccountUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.Collects_Account
    template_name = 'recursos_humanos/cuts/collects/upload.html'
    form_class = forms.ColletcAcountUploadForm
    success_url = "../../"
    pk_url_kwarg = 'pk_collect_account'

    def dispatch(self, request, *args, **kwargs):

        self.cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        self.collec_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
                "usuarios.recursos_humanos.cortes.cuentas_cobro.ver",
                "usuarios.recursos_humanos.cortes.cuentas_cobro.cargar"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('cargar_cuentas_cobro')):
                if self.collec_account.estate == 'Creado' or self.collec_account.estate == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Cargado'
        self.object.save()

        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        models.Registration.objects.create(
            cut=collect_account.cut,
            user=self.request.user,
            collect_account=collect_account,
            delta="Cargo documentos desde el modulo Recursos humanos"
        )

        return super(CollectAccountUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTA DE COBRO CONTRATO {0}".format(self.collec_account.contract.nombre)
        kwargs['breadcrum_1'] = self.cut.consecutive
        kwargs['breadcrum_active'] = self.collec_account.contract.nombre
        kwargs['file3_url'] = self.collec_account.pretty_print_url_file3()
        kwargs['file4_url'] = self.collec_account.pretty_print_url_file4()
        kwargs['file5_url'] = self.collec_account.pretty_print_url_file5()
        return super(CollectAccountUploadView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk_cut':self.kwargs['pk_cut'],
                'pk_collect_account':self.kwargs['pk_collect_account'],}

class CollectAccountApprobView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])


        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.collect_account.estate = 'Aprobado'
                    self.collect_account.save()

                    collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

                    models.Registration.objects.create(
                        cut=collect_account.cut,
                        user=self.request.user,
                        collect_account=collect_account,
                        delta="Aprobo la seguridad social"
                    )
                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.collect_account.estate = 'Aprobado'
                        self.collect_account.save()

                        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

                        models.Registration.objects.create(
                            cut=collect_account.cut,
                            user=self.request.user,
                            collect_account=collect_account,
                            delta="Aprobo la seguridad social"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class CollectAccountRejectView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/individual/territorios/comunity/ruta/hogares/momento/reject.html'
    form_class = forms.CollectsAccountRejectForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):

        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        if collect_account.estate != 'Rechazado':
            collect_account.estate = 'Rechazado'
            collect_account.observaciones = form.cleaned_data['observaciones']
            collect_account.save()

            collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

            models.Registration.objects.create(
                cut=collect_account.cut,
                user=self.request.user,
                collect_account=collect_account,
                delta="Rechazo la seguridad social por: " + collect_account.observaciones
            )

            user = collect_account.contract.get_user_or_none()

            if user != None:
                tasks.send_mail_templated_cuenta_cobro(
                    'mail/recursos_humanos/reject_ss.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'Contrato': collect_account.contract.nombre,
                        'nombre': collect_account.contract.contratista.nombres,
                        'nombre_completo': collect_account.contract.contratista.get_full_name(),
                        'valor': '$ {:20,.2f}'.format(collect_account.value_fees.amount),
                        'observaciones': collect_account.observaciones,
                    },
                    DEFAULT_FROM_EMAIL,
                    [user.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )


        return super(CollectAccountRejectView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        cuts = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        kwargs['title'] = "Rechazar Seguridad social"
        kwargs['breadcrum_1'] = cuts.consecutive


        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(CollectAccountRejectView, self).get_context_data(**kwargs)

class CollectAccountDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        cut = models.Cuts.objects.get(id = self.kwargs['pk_cut'])
        cuenta_cobro = models.Collects_Account.objects.get(id = self.kwargs['pk_collect_account'])
        registers= models.Registration.objects.filter(collect_account=cuenta_cobro)
        registers.delete()
        cuenta_cobro.delete()


        return HttpResponseRedirect('../../')


class CutsCollectsReportAccountView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.cortes.ver",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        cuts = Cuts.objects.get(id=self.kwargs['pk_cut'])
        id_cuts = cuts.id
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Reporte del corte ' + str(cuts.consecutive),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_list_collects_account.delay(reporte.id,id_cuts)

        return HttpResponseRedirect('/reportes/')


class CutsReport(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.cortes.ver",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Listado de cortes y cuentas de cobro',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_list_collects_account.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')


#----------------------------------------------------------------------------------

#-------------------------------Liquidaciones--------------------------------------

class LiquidationsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.recursos_humanos.liquidaciones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/liquidations/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Liquidaciones"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/liquidations/'
        return super(LiquidationsListView,self).get_context_data(**kwargs)

class LiquidationsCreateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      FormView):

    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/liquidations/create.html'
    form_class = forms.CreateLiquidationForm
    success_url = '../../'

    permissions = {
        "all": [
            "usuarios.recursos_humanos.liquidaciones.ver"
        ]
    }

    def get_cuentas_fees(self):
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contract'])
        accounts = models.Collects_Account.objects.filter(contract=contrato).exclude(liquidacion=True)
        list= ''
        count= accounts.count()

        for account in accounts:
            month = account.month
            year = account.year
            value = account.value_fees
            cut = account.cut.consecutive
            list += '<p><b>Corte: </b>{0}</p><p><b>Fecha: </b>{1} - {2}</p><ul>{3}</ul>'.format(cut,month,year,value)

        return list

    def get_context_data(self, **kwargs):
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contract'])
        cuentas = models.Collects_Account.objects.filter(contract=contrato)
        total_valor = cuentas.aggregate(Sum('value_fees'))['value_fees__sum']
        if total_valor == None:
            total_valor = 0

        valor_pagar = float(contrato.valor) - float(total_valor)

        kwargs['title'] = "LIQUIDACION - Contrato: {0}".format(contrato.nombre)
        kwargs['breadcrum_active'] = contrato.nombre
        kwargs['valor'] = contrato.pretty_print_valor()
        kwargs['contratista'] = contrato.contratista.get_full_name()
        kwargs['contrato'] = contrato.nombre
        kwargs['inicio'] = contrato.inicio
        kwargs['fin'] = contrato.pretty_print_fin()
        kwargs['cuentas'] = self.get_cuentas_fees()
        kwargs['valor_pagar'] = "${:,.2f}".format(valor_pagar)

        return super(LiquidationsCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        contrato = models.Contratos.objects.get(id=self.kwargs['pk_contract'])
        fecha = timezone.now()

        cuentas = models.Collects_Account.objects.filter(contract=contrato)
        total_valor = cuentas.aggregate(Sum('value_fees'))['value_fees__sum']

        if total_valor == None:
            total_valor=0

        Valor_pagar = float(contrato.valor) - float(total_valor)


        if float(contrato.valor) <= float(total_valor):
            liquidacion, created = models.Liquidations.objects.get_or_create(
                contrato=contrato,
                valor_ejecutado = contrato.valor,
                valor = 0,
                estado="Generada",
                estado_seguridad="Generada",
                estado_informe="Generada",
                fecha_actualizacion=timezone.now(),
                usuario_actualizacion=self.request.user,
                mes = form.cleaned_data['mes'],
                año = form.cleaned_data['año'],
            )
            contrato.liquidado = True
            contrato.save()

            fecha_inicio = functions.contrato_inicio_español(contrato.id)
            fecha_fin = functions.contrato_fin_español(contrato.id)

            template_header = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/liquidacion.html', 'rb'),
                "html.parser")

            template_header_tag = template_header.find(class_='contratista_contrato_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre).upper())

            template_header_tag = template_header.find(class_='contratista_nombre_span_1')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag = template_header.find(class_='contratista_cedula_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_objeto_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.objeto_contrato))

            template_header_tag = template_header.find(class_='contrato_valor_total_span_1')
            template_header_tag.insert(1, liquidacion.contrato.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_valor_otros_si_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_otros())

            template_header_tag = template_header.find(class_='contrato_valor_total_span_2')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_ejecutado())

            template_header_tag = template_header.find(class_='contrato_valor_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_inicio_span_1')
            template_header_tag.insert(1, fecha_inicio)

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_1')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_2')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_2')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contrato_codigo_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre))

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_2')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_3')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_3')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_cargo_span')
            template_header_tag.insert(1, str(liquidacion.contrato.cargo.nombre))

            liquidacion.html.save('liquidacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

            path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

            liquidacion.file.save('liquidacion.pdf',
                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

            if settings:
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                pdfkit.from_file([liquidacion.html.path], liquidacion.file.path, {
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }, configuration=config)
            else:
                data = pdfkit.from_url(
                    url=[liquidacion.html.url,liquidacion.html2.url],
                    output_path=False,
                    options={
                        '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                        '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                        '--enable-local-file-access': None,
                        '--page-size': 'Letter'
                    }
                )
                liquidacion.file.save('liquidacion.pdf', File(io.BytesIO(data)))


            """
            usuario = contrato.get_user_or_none()

            if usuario != None:
                tasks.send_mail_templated_liquidacion(
                    'mail/cpe_2018/cuenta_cobro.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': contrato.nombre,
                        'nombre': contrato.contratista.nombres,
                        'nombre_completo': contrato.contratista.get_full_name(),
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )
            """

        elif float(contrato.valor) > float(total_valor):
            visible = form.cleaned_data['visible']
            desctivar_valores = form.cleaned_data['visible_two']



            if visible==False:
                liquidacion, created = models.Liquidations.objects.get_or_create(
                    contrato=contrato,
                    valor_ejecutado=contrato.valor,
                    valor=Valor_pagar,
                    estado="Generada",
                    estado_seguridad="Generada",
                    estado_informe="Generada",
                    fecha_actualizacion=timezone.now(),
                    usuario_actualizacion=self.request.user,
                    mes=form.cleaned_data['mes'],
                    año=form.cleaned_data['año'],
                    visible= True,
                )

            else:
                valor_pagar = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))
                total_ejecutado = float(total_valor) + float(valor_pagar)

                liquidacion, created = models.Liquidations.objects.get_or_create(
                    contrato=contrato,
                    valor_ejecutado=total_ejecutado,
                    valor=valor_pagar,
                    estado="Generada",
                    estado_seguridad="Generada",
                    estado_informe="Generada",
                    fecha_actualizacion=timezone.now(),
                    usuario_actualizacion=self.request.user,
                    mes=form.cleaned_data['mes'],
                    año=form.cleaned_data['año'],
                )

            contrato.liquidado = True
            contrato.save()

            if desctivar_valores==True:
                otros = models.Otros_si.objects.filter(contrato=contrato).count()
                liquidacion.desctivar_valores = True

                if otros > 0:
                    otros_si = models.Otros_si.objects.filter(contrato=contrato)
                    valor_otros_si = otros_si.aggregate(Sum('valor'))['valor__sum']
                    liquidacion.valor_contrato = float(form.cleaned_data['valor_contrato'].replace('$ ', '').replace(',', ''))
                    liquidacion.valor_otros = float(valor_otros_si)
                else:
                    liquidacion.valor_otros = 0
                liquidacion.save()


            fecha_inicio = functions.contrato_inicio_español(contrato.id)
            fecha_fin = functions.contrato_fin_español(contrato.id)

            template_header = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/liquidacion.html', 'rb'),
                "html.parser")

            template_header_tag = template_header.find(class_='contratista_contrato_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre).upper())

            template_header_tag = template_header.find(class_='contratista_nombre_span_1')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag = template_header.find(class_='contratista_cedula_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_objeto_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.objeto_contrato))

            template_header_tag = template_header.find(class_='contrato_valor_total_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_contrato())

            template_header_tag = template_header.find(class_='contrato_valor_otros_si_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_otros())

            template_header_tag = template_header.find(class_='contrato_valor_total_span_2')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_ejecutado())

            template_header_tag = template_header.find(class_='contrato_valor_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_inicio_span_1')
            template_header_tag.insert(1, fecha_inicio)

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_1')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_2')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_2')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contrato_codigo_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre))

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_2')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_3')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_3')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_cargo_span')
            template_header_tag.insert(1, str(liquidacion.contrato.cargo.nombre))

            liquidacion.html.save('liquidacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

            liquidacion.file.save('liquidacion.pdf',
                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))




            collect_count = models.Collects_Account.objects.filter(contract=contrato).count()
            number = collect_count + 1

            value_money = float(liquidacion.valor)
            value_letter_num = value_money
            value_letter = numero_to_letras(int(value_letter_num))

            template_header_2 = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'), "html.parser")

            template_header_tag_2 = template_header_2.find(class_='fecha_span')
            template_header_tag_2.insert(1, liquidacion.pretty_creation_datetime())

            template_header_tag_2 = template_header_2.find(class_='number_span')
            template_header_tag_2.insert(1, str(number))

            template_header_tag_2 = template_header_2.find(class_='contract_span')
            template_header_tag_2.insert(1, liquidacion.contrato.nombre)

            template_header_tag_2 = template_header_2.find(class_='contractor_name_span')
            template_header_tag_2.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag_2 = template_header_2.find(class_='contractor_document_span')
            template_header_tag_2.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag_2 = template_header_2.find(class_='contractor_name_firm')
            template_header_tag_2.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag_2 = template_header_2.find(class_='contractor_document_firm')
            template_header_tag_2.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag_2 = template_header_2.find(class_='value_letter_span')
            template_header_tag_2.insert(1, value_letter)

            template_header_tag_2 = template_header_2.find(class_='value_letter_num_span')
            template_header_tag_2.insert(1, str(value_letter_num))

            template_header_tag_2 = template_header_2.find(class_='position_span')
            template_header_tag_2.insert(1, str(liquidacion.contrato.get_cargo()))

            template_header_tag_2 = template_header_2.find(class_='month_span')
            template_header_tag_2.insert(1, str(liquidacion.mes))

            template_header_tag_2 = template_header_2.find(class_='year_span')
            template_header_tag_2.insert(1, str(liquidacion.año))

            liquidacion.html2.save('cuenta_cobro.html', File(io.BytesIO(template_header_2.prettify(encoding='utf-8'))))
            path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


            if settings.DEBUG:
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                pdfkit.from_file([liquidacion.html.path,liquidacion.html2.path], liquidacion.file.path, {
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }, configuration=config)
            else:
                data = pdfkit.from_url(
                    url=[liquidacion.html.url,liquidacion.html2.url],
                    output_path=False,
                    options={
                        '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                        '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                        '--enable-local-file-access': None,
                        '--page-size': 'Letter'
                    }
                )
                liquidacion.file.save('liquidacion.pdf', File(io.BytesIO(data)))



            """
            usuario = contrato.get_user_or_none()

            if usuario != None:
                tasks.send_mail_templated_liquidacion(
                    'mail/cpe_2018/cuenta_cobro.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': contrato.nombre,
                        'nombre': contrato.contratista.nombres,
                        'nombre_completo': contrato.contratista.get_full_name(),
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )
            """

        models.Collects_Account.objects.create(
            contract=contrato,
            user_creation=self.request.user,
            value_fees=liquidacion.valor,
            month=form.cleaned_data['mes'],
            year=form.cleaned_data['año'],
            file=liquidacion.file,
            liquidacion=True,
            estate="Generado",
            estate_inform="Generado",
            estate_report="Generado",
        )

        return super(LiquidationsCreateView,self).form_valid(form)

    def get_initial(self):
        return {'pk_contract':self.kwargs['pk_contract']}

class LiquidationsEditView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      FormView):

    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/liquidations/edit.html'
    form_class = forms.EditLiquidationForm
    success_url = '../../'

    permissions = {
        "all": [
            "usuarios.recursos_humanos.liquidaciones.ver"
        ]
    }

    def get_cuentas_fees(self):
        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        contrato = liquidacion.contrato
        accounts = models.Collects_Account.objects.filter(contract=contrato).exclude(liquidacion=True)
        list= ''
        count= accounts.count()

        for account in accounts:
            month = account.month
            year = account.year
            value = account.value_fees
            cut = account.cut.consecutive

            list += '<p><b>Corte: </b>{0}</p><p><b>Fecha: </b>{1} - {2}</p><ul>{3}</ul>'.format(cut,month,year,value)

        return list

    def get_context_data(self, **kwargs):
        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        contrato = liquidacion.contrato
        cuentas = models.Collects_Account.objects.filter(contract=contrato)
        total_valor = cuentas.aggregate(Sum('value_fees'))['value_fees__sum']
        if total_valor == None:
            total_valor = 0

        valor_pagar = float(contrato.valor) - float(total_valor)

        kwargs['title'] = "LIQUIDACION - Contrato: {0}".format(contrato.nombre)
        kwargs['breadcrum_active'] = contrato.nombre
        kwargs['valor'] = contrato.pretty_print_valor()
        kwargs['contratista'] = contrato.contratista.get_full_name()
        kwargs['contrato'] = contrato.nombre
        kwargs['inicio'] = contrato.inicio
        kwargs['fin'] = contrato.pretty_print_fin()
        kwargs['cuentas'] = self.get_cuentas_fees()
        kwargs['valor_pagar'] = "${:,.2f}".format(valor_pagar)

        return super(LiquidationsEditView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        contrato = liquidacion.contrato
        fecha = timezone.now()

        cuentas = models.Collects_Account.objects.filter(contract=contrato)
        total_valor = cuentas.aggregate(Sum('value_fees'))['value_fees__sum']
        total_valor = float(total_valor) - float(liquidacion.valor)

        Valor_pagar = float(contrato.valor) - float(total_valor)


        if float(contrato.valor) <= float(total_valor):
            liquidacion.valor_ejecutado = float(contrato.valor)
            liquidacion.valor = 0
            liquidacion.estado="Generada"
            liquidacion.estado_informe="Generada"
            liquidacion.estado_seguridad="Generada"
            liquidacion.fecha_actualizacion=timezone.now()
            liquidacion.usuario_actualizacion=self.request.user
            liquidacion.save()

            liquidacion.file.delete()

            fecha_inicio = functions.contrato_inicio_español(contrato.id)
            fecha_fin = functions.contrato_fin_español(contrato.id)

            template_header = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/liquidacion.html', 'rb'),
                "html.parser")

            template_header_tag = template_header.find(class_='contratista_contrato_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre).upper())

            template_header_tag = template_header.find(class_='contratista_nombre_span_1')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag = template_header.find(class_='contratista_cedula_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_objeto_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.objeto_contrato))

            template_header_tag = template_header.find(class_='contrato_valor_total_span_1')
            template_header_tag.insert(1, liquidacion.contrato.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_valor_total_span_2')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_ejecutado())

            template_header_tag = template_header.find(class_='contrato_valor_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_inicio_span_1')
            template_header_tag.insert(1, fecha_inicio)

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_1')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_2')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_2')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contrato_codigo_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre))

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_2')
            template_header_tag.insert(1, liquidacion.contrato.fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_3')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_3')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_cargo_span')
            template_header_tag.insert(1, str(liquidacion.contrato.cargo.nombre))

            liquidacion.html.save('liquidacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

            path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

            liquidacion.file.save('liquidacion.pdf',
                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

            if settings.DEBUG:
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                pdfkit.from_file([liquidacion.html.path], liquidacion.file.path, {
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }, configuration=config)
            else:
                data = pdfkit.from_url(
                    url=liquidacion.html.url,
                    output_path=False,
                    options={
                        '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                        '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                        '--enable-local-file-access': None,
                        '--page-size': 'Letter'
                    }
                )
                liquidacion.file.save('liquidacion.pdf', File(io.BytesIO(data)))


            """
            usuario = contrato.get_user_or_none()

            if usuario != None:
                tasks.send_mail_templated_liquidacion(
                    'mail/cpe_2018/cuenta_cobro.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': contrato.nombre,
                        'nombre': contrato.contratista.nombres,
                        'nombre_completo': contrato.contratista.get_full_name(),
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )
            """

        elif float(contrato.valor) > float(total_valor):
            visible = form.cleaned_data['visible']

            if visible==False:
                liquidacion.valor_ejecutado=float(contrato.valor)
                liquidacion.valor=float(Valor_pagar)
                liquidacion.estado="Generada"
                liquidacion.estado_informe = "Generada"
                liquidacion.estado_seguridad = "Generada"
                liquidacion.fecha_actualizacion=timezone.now()
                liquidacion.usuario_actualizacion=self.request.user
                liquidacion.mes=form.cleaned_data['mes']
                liquidacion.año=form.cleaned_data['año']
                liquidacion.visible=form.cleaned_data['visible']
                liquidacion.desctivar_valores=form.cleaned_data['visible_two']
                liquidacion.save()
            else:
                valor_pagar = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))
                total_ejecutado = float(total_valor) + float(valor_pagar)
                liquidacion.valor_ejecutado=total_ejecutado
                liquidacion.valor=valor_pagar
                liquidacion.estado="Generada"
                liquidacion.estado_informe = "Generada"
                liquidacion.estado_seguridad = "Generada"
                liquidacion.fecha_actualizacion=timezone.now()
                liquidacion.usuario_actualizacion=self.request.user
                liquidacion.mes=form.cleaned_data['mes']
                liquidacion.año=form.cleaned_data['año']
                liquidacion.visible = form.cleaned_data['visible']
                liquidacion.desctivar_valores = form.cleaned_data['visible_two']
                liquidacion.save()


            liquidacion.file.delete()

            fecha_inicio = functions.contrato_inicio_español(contrato.id)
            fecha_fin = functions.contrato_fin_español(contrato.id)

            if liquidacion.desctivar_valores==True:
                otros = models.Otros_si.objects.filter(contrato=liquidacion.contrato).count()
                liquidacion.desctivar_valores = True

                if otros > 0:
                    otros_si = models.Otros_si.objects.filter(contrato=liquidacion.contrato)
                    valor_otros_si = otros_si.aggregate(Sum('valor'))['valor__sum']
                    liquidacion.valor_contrato = float(form.cleaned_data['valor_contrato'].replace('$ ', '').replace(',', ''))
                    liquidacion.valor_otros = float(valor_otros_si)
                else:
                    liquidacion.valor_otros = 0
                liquidacion.save()

            template_header = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/liquidacion.html', 'rb'),
                "html.parser")

            template_header_tag = template_header.find(class_='contratista_contrato_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre).upper())

            template_header_tag = template_header.find(class_='contratista_nombre_span_1')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag = template_header.find(class_='contratista_cedula_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_objeto_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.objeto_contrato))

            template_header_tag = template_header.find(class_='contrato_valor_total_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_contrato())

            template_header_tag = template_header.find(class_='contrato_valor_otros_si_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_otros())

            template_header_tag = template_header.find(class_='contrato_valor_total_span_2')
            template_header_tag.insert(1, liquidacion.pretty_print_valor_ejecutado())

            template_header_tag = template_header.find(class_='contrato_valor_span_1')
            template_header_tag.insert(1, liquidacion.pretty_print_valor())

            template_header_tag = template_header.find(class_='contrato_inicio_span_1')
            template_header_tag.insert(1, fecha_inicio)

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_1')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_2')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_2')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contrato_codigo_span_1')
            template_header_tag.insert(1, str(liquidacion.contrato.nombre))

            template_header_tag = template_header.find(class_='contrato_finalizacion_span_2')
            template_header_tag.insert(1, fecha_fin)

            template_header_tag = template_header.find(class_='contratista_nombre_span_3')
            template_header_tag.insert(1, liquidacion.contrato.contratista.get_full_name().upper())

            template_header_tag = template_header.find(class_='contratista_cedula_span_3')
            template_header_tag.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag = template_header.find(class_='contratista_cargo_span')
            template_header_tag.insert(1, str(liquidacion.contrato.cargo.nombre))

            liquidacion.html.save('liquidacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

            liquidacion.file.save('liquidacion.pdf',
                                  File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))




            collect_count = models.Collects_Account.objects.filter(contract=contrato).count()
            number = collect_count + 1

            value_money = float(liquidacion.valor)
            value_letter_num = value_money
            value_letter = numero_to_letras(int(value_letter_num))

            template_header_2 = BeautifulSoup(
                open(settings.STATICFILES_DIRS[0] + '/pdfkit/cuentas_cobro/cuenta.html', 'rb'), "html.parser")

            template_header_tag_2 = template_header_2.find(class_='fecha_span')
            template_header_tag_2.insert(1, liquidacion.pretty_creation_datetime())

            template_header_tag_2 = template_header_2.find(class_='number_span')
            template_header_tag_2.insert(1, str(number))

            template_header_tag_2 = template_header_2.find(class_='contract_span')
            template_header_tag_2.insert(1, liquidacion.contrato.nombre)

            template_header_tag_2 = template_header_2.find(class_='contractor_name_span')
            template_header_tag_2.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag_2 = template_header_2.find(class_='contractor_document_span')
            template_header_tag_2.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag_2 = template_header_2.find(class_='contractor_name_firm')
            template_header_tag_2.insert(1, liquidacion.contrato.contratista.get_full_name())

            template_header_tag_2 = template_header_2.find(class_='contractor_document_firm')
            template_header_tag_2.insert(1, str(liquidacion.contrato.contratista.cedula))

            template_header_tag_2 = template_header_2.find(class_='value_letter_span')
            template_header_tag_2.insert(1, value_letter)

            template_header_tag_2 = template_header_2.find(class_='value_letter_num_span')
            template_header_tag_2.insert(1, str(value_letter_num))

            template_header_tag_2 = template_header_2.find(class_='position_span')
            template_header_tag_2.insert(1, str(liquidacion.contrato.get_cargo()))

            template_header_tag_2 = template_header_2.find(class_='month_span')
            template_header_tag_2.insert(1, str(liquidacion.mes))

            template_header_tag_2 = template_header_2.find(class_='year_span')
            template_header_tag_2.insert(1, str(liquidacion.año))

            liquidacion.html2.save('cuenta_cobro.html', File(io.BytesIO(template_header_2.prettify(encoding='utf-8'))))
            path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


            if settings.DEBUG:
                config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
                pdfkit.from_file([liquidacion.html.path,liquidacion.html2.path], liquidacion.file.path, {
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }, configuration=config)
            else:
                data = pdfkit.from_url(
                    url=[liquidacion.html.url,liquidacion.html2.url],
                    output_path=False,
                    options={
                        '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/header/header.html',
                        '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/liquidaciones/footer/footer.html',
                        '--enable-local-file-access': None,
                        '--page-size': 'Letter'
                    }
                )
                liquidacion.file.save('liquidacion.pdf', File(io.BytesIO(data)))



            """
            usuario = contrato.get_user_or_none()

            if usuario != None:
                tasks.send_mail_templated_liquidacion(
                    'mail/cpe_2018/cuenta_cobro.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': contrato.nombre,
                        'nombre': contrato.contratista.nombres,
                        'nombre_completo': contrato.contratista.get_full_name(),
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )
            """

        cuenta_cobro = Collects_Account.objects.get(contract=contrato, liquidacion=True)
        cuenta_cobro.value_fees = liquidacion.valor
        cuenta_cobro.month = liquidacion.mes
        cuenta_cobro.year = liquidacion.año
        cuenta_cobro.file = liquidacion.file
        cuenta_cobro.liquidacion = True
        cuenta_cobro.estate = "Generado"
        cuenta_cobro.estate_inform = "Generado"
        cuenta_cobro.estate_report = "Generado"
        cuenta_cobro.save()

        return super(LiquidationsEditView,self).form_valid(form)

    def get_initial(self):
        return {'pk_liquidacion':self.kwargs['pk_liquidacion']}

class LiquidationsDelete(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.liquidaciones.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        contrato = liquidacion.contrato

        cuenta = models.Collects_Account.objects.filter(contract=contrato,liquidacion=True)
        registro=models.Registration.objects.filter(collect_account=cuenta)
        if cuenta:
            registro.delete()
            cuenta.delete()
        contrato.liquidado = False
        contrato.save()
        liquidacion.delete()

        return HttpResponseRedirect('../../')

class LiquidationsAporbarSeguridad(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])


        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.liquidaciones.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.liquidacion.estado_seguridad = 'Aprobado'
                    self.liquidacion.save()

                    liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                    cuenta = models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                    cuenta.estate="Aprobado"
                    cuenta.save()

                    models.Registration.objects.create(
                        cut=cuenta.cut,
                        user=self.request.user,
                        collect_account=cuenta,
                        delta="Aprobo la seguridad social de la liquidacion"
                    )
                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.liquidacion.estado_seguridad = 'Aprobado'
                        self.liquidacion.save()


                        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                        cuenta = models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                        cuenta.estate = "Aprobado"
                        cuenta.save()

                        models.Registration.objects.create(
                            cut=cuenta.cut,
                            user=self.request.user,
                            collect_account=cuenta,
                            delta="Aprobo la seguridad social de la liquidacion"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class LiquidationsRechazarSeguridad(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])


        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.liquidaciones.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.liquidacion.estado_seguridad = 'Rechazado'
                    self.liquidacion.save()

                    liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                    cuenta = models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                    cuenta.estate="Rechazado"
                    cuenta.save()

                    models.Registration.objects.create(
                        cut=cuenta.cut,
                        user=self.request.user,
                        collect_account=cuenta,
                        delta="Rechazo la seguridad social de la liquidacion"
                    )
                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.liquidacion.estado_seguridad = 'Rechazado'
                        self.liquidacion.save()


                        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                        cuenta = models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                        cuenta.estate = "Rechazado"
                        cuenta.save()

                        models.Registration.objects.create(
                            cut=cuenta.cut,
                            user=self.request.user,
                            collect_account=cuenta,
                            delta="Rechazo la seguridad social de la liquidacion"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class LiquidationsHistorialSeguridad(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,TemplateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.ver",
            "usuarios.recursos_humanos.liquidaciones.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/liquidations/historial.html'

    def get_items_registers(self):

        list = []
        liquidacion = models.Liquidations.objects.get(id= self.kwargs['pk_liquidacion'])

        cuenta= models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)

        registers = models.Registration.objects.filter(collect_account=cuenta).order_by('-creation')

        for register in registers:
            list.append({
                'propio': True if register.user == self.request.user else False,
                'fecha': register.pretty_creation_datetime(),
                'usuario': register.user.get_full_name_string(),
                'html': register.delta,
            })

        return list

    def get_context_data(self, **kwargs):
        registers = self.get_items_registers()
        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        collect_account = models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
        kwargs['title'] = "GESTIÓN"
        kwargs['registros'] = registers
        kwargs['registros_cantidad'] = len(registers)
        kwargs['breadcrum_active'] = collect_account.contract.nombre
        return super(LiquidationsHistorialSeguridad,self).get_context_data(**kwargs)

class LiquidationsUpload(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.Liquidations
    template_name = 'recursos_humanos/liquidations/upload.html'
    form_class = forms.LiquidationsploadForm
    success_url = "../../"
    pk_url_kwarg = 'pk_liquidacion'

    def dispatch(self, request, *args, **kwargs):

        self.liquidation = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])

        self.permissions = {
            "all": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.liquidacion.ver",
                "usuarios.recursos_humanos.liquidacion.cargar"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Cargado'
        self.object.estado_informe = 'Generada'
        self.object.estado_seguridad = 'Generada'
        self.object.save()

        liquidacion = models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        cuenta_cobro = models.Collects_Account.objects.filter(contract=liquidacion.contrato, liquidacion=True).first()

        cuenta_cobro.estate = "Generada"
        cuenta_cobro.estate_inform = "Generada"
        cuenta_cobro.estate_report ="Cargado"

        cuenta_cobro.file3=liquidacion.file2
        cuenta_cobro.file4=liquidacion.file3
        cuenta_cobro.file5=liquidacion.file4

        cuenta_cobro.save()

        return super(LiquidationsUpload, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "LIQUIDACION DEL CONTRATO {0}".format(self.liquidation.contrato.nombre)
        kwargs['breadcrum_active'] = self.liquidation.contrato.nombre
        kwargs['file3_url'] = self.liquidation.pretty_print_url_file3()
        kwargs['file4_url'] = self.liquidation.pretty_print_url_file4()
        kwargs['file2_url'] = self.liquidation.pretty_print_url_file2()
        return super(LiquidationsUpload,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk_liquidacion':self.kwargs['pk_liquidacion']}


#----------------------------------------------------------------------------------

#------------------------------------ CARGOS --------------------------------------

class CargosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.recursos_humanos.cargos.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cargos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Cargos"
        kwargs['url_datatable'] = '/rest/v1.0/recursos_humanos/cargos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.cargos.crear')
        return super(CargosListView,self).get_context_data(**kwargs)

class CargosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.recursos_humanos.cargos.ver",
            "usuarios.recursos_humanos.cargos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cargos/crear.html'
    form_class = forms.CargoForm
    success_url = "../"
    model = models.Cargos

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR CARGO"
        return super(CargosCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(CargosCreateView, self).form_valid(form)

class CargosupdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.recursos_humanos.cargos.ver",
            "usuarios.recursos_humanos.cargos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cargos/editar.html'
    form_class = forms.CargoForm
    success_url = "../../"
    model = models.Cargos


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR CARGO"
        kwargs['breadcrum_active'] = models.Cargos.objects.get(id=self.kwargs['pk']).nombre
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.recursos_humanos.cargo.crear')
        return super(CargosupdateView,self).get_context_data(**kwargs)