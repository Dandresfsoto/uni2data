from django.db.models import Sum
from django.views.generic import TemplateView, CreateView, UpdateView, View, FormView
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import forms, models
from django.shortcuts import redirect
import io
import pdfkit
from django.core.files import File
from delta import html
import json
from bs4 import BeautifulSoup
import os

from recursos_humanos.models import Collects_Account, Contratos
from recursos_humanos.tasks import send_mail_templated_certificacion
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_DIRECCION_FINANCIERA
import mimetypes
from django.http import HttpResponseRedirect
from recursos_humanos import tasks
from reportes.models import Reportes
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms
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

        if form.cleaned_data['firma'] == 'Director administrativo y financiero':

            template_no_header = BeautifulSoup(open(settings.TEMPLATES[0]['DIRS'][
                                          0] + '/pdfkit/certificaciones/no_header/certificacion_direccion_financiera.html',
                                      'rb'), "html.parser")

            template_header = BeautifulSoup(open(settings.TEMPLATES[0]['DIRS'][
                                          0] + '/pdfkit/certificaciones/header/certificacion_direccion_financiera.html',
                                      'rb'), "html.parser")

        elif form.cleaned_data['firma'] == 'Gerencia':

            template_no_header = BeautifulSoup(
                open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/no_header/certificacion_gerencia.html',
                     'rb'), "html.parser")

            template_header = BeautifulSoup(
                open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/header/certificacion_gerencia.html',
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
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        pdfkit.from_file(certifiacion.html.path, certifiacion.pdf.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\footer\\footer.html',
            '--page-size':'Letter'
        }, configuration=config)

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

        if form.cleaned_data['firma'] == 'Director administrativo y financiero':

            template_no_header = BeautifulSoup(open(settings.TEMPLATES[0]['DIRS'][
                                          0] + '/pdfkit/certificaciones/no_header/certificacion_direccion_financiera.html',
                                      'rb'), "html.parser")

            template_header = BeautifulSoup(open(settings.TEMPLATES[0]['DIRS'][
                                          0] + '/pdfkit/certificaciones/header/certificacion_direccion_financiera.html',
                                      'rb'), "html.parser")

        elif form.cleaned_data['firma'] == 'Gerencia':

            template_no_header = BeautifulSoup(
                open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/no_header/certificacion_gerencia.html',
                     'rb'), "html.parser")

            template_header = BeautifulSoup(
                open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/header/certificacion_gerencia.html',
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
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        pdfkit.from_file(certifiacion.html.path, certifiacion.pdf.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\footer\\footer.html',
            '--page-size':'Letter'
        }, configuration=config)

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
            "usuarios.recurso_humano.ver",
            "usuarios.recurso_humano.cortes.ver"
        ],
        "crear": [
            "usuarios.recurso_humano.ver",
            "usuarios.recurso_humano.cortes.ver",
            "usuarios.recurso_humano.cortes.crear"
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
                "usuarios.recurso_humano.ver",
                "usuarios.recurso_humano.cortes.ver",
                "usuarios.recurso_humano.cortes.crear"
            ]
        }
        return permissions

    def form_valid(self, form):

        cut = models.Cuts.objects.create(
            consecutive = models.Cuts.objects.all().count() + 1,
            user_creation = self.request.user,
            name = form.cleaned_data['name']
        )

        contracts_ids = models.Contratos.objects.exclude(liquidado = True).filter(ejecucion = True, suscrito=True).values_list('id',flat=True).distinct()
        user = self.request.user

        for contract_id in contracts_ids:
            contract = models.Contratos.objects.get(id=contract_id)
            if form.cleaned_data['contrato_{0}'.format(contract.id)]:
                models.Collects_Account.objects.create(
                    contract=contract,
                    cut=cut,
                    user_creation=user,
                    estate='Creado',
                    value=0
                )


        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CORTE DE PAGO"
        return super(CutsCreateView,self).get_context_data(**kwargs)

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
        return super(CutsCollectsAccountView,self).get_context_data(**kwargs)


class CollectAccountUpdateView(FormView):
    login_url = settings.LOGIN_URL
    template_name = 'recursos_humanos/cuts/collects/update.html'
    form_class = forms.CollectsAccountForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        self.collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.recursos_humanos.ver",
                "usuarios.recursos_humanos.cortes.ver",
                "usuarios.recursos_humanos.cortes.cuentas_cobro.ver",
                "usuarios.recursos_humanos.cortes.cuentas_cobro.editar"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('cargar_cuentas_cobro')):
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

    def form_valid(self, form):

        cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        cuenta_cobro.data_json = json.dumps({'mes': form.cleaned_data['mes'], 'year': form.cleaned_data['year']})
        cuenta_cobro.valores_json = form.cleaned_data['valores']
        cuenta_cobro.save()

        cuenta_cobro.file.delete()
        cuenta_cobro.html.delete()

        cuenta_cobro.create_delta()

        delta_valores = json.loads(cuenta_cobro.valores_json)

        renders = ''

        if len(delta_valores) > 1:

            for cuenta in delta_valores:
                valor = float(cuenta.get('valor').replace('$ ', '').replace(',', ''))
                mes = cuenta.get('mes')
                year = cuenta.get('year')
                renders += '<div class="hoja">' + html.render(
                    functions.delta_cuenta_cobro_parcial(cuenta_cobro, valor, mes, year)['ops']) + '</div>'

        else:
            renders = '<div class="hoja">' + html.render(
                functions.delta_cuenta_cobro_parcial(cuenta_cobro, float(cuenta_cobro.valor.amount),
                                                     form.cleaned_data['mes'][0], form.cleaned_data['year'])[
                    'ops']) + '</div>'

        html_render = BeautifulSoup(renders, "html.parser", from_encoding='utf-8')

        template_no_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/no_header/cuenta_cobro.html',
                 'rb'), "html.parser")

        template_no_header_tag = template_no_header.find(class_='inserts')
        template_no_header_tag.insert(1, html_render)

        cuenta_cobro.html.save('cuenta_cobro.html', File(io.BytesIO(template_no_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        cuenta_cobro.file.save('cuenta_cobro.pdf',
                               File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        options = {
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }

        pdfkit.from_file(cuenta_cobro.html.path, cuenta_cobro.file.path, options, configuration=config)

        if cuenta_cobro.estado != 'Cargado':
            cuenta_cobro.estado = 'Generado'
        cuenta_cobro.save()

        usuario = cuenta_cobro.ruta.contrato.get_user_or_none()

        if usuario != None:
            tasks.send_mail_templated_cuenta_cobro(
                'mail/cpe_2018/cuenta_cobro.tpl',
                {
                    'url_base': 'https://' + self.request.META['HTTP_HOST'],
                    'ruta': cuenta_cobro.ruta.nombre,
                    'nombre': cuenta_cobro.ruta.contrato.contratista.nombres,
                    'nombre_completo': cuenta_cobro.ruta.contrato.contratista.get_full_name(),
                    'valor': '$ {:20,.2f}'.format(cuenta_cobro.valor.amount),
                },
                DEFAULT_FROM_EMAIL,
                [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_cuentas_meses(self):

        accounts = models.Collects_Account.objects.filter(contract=self.collect_account.contract).exclude(id=self.collect_account.id)
        data = {}
        for account in accounts:
            delta_valores = json.loads(collect_account.valores_json)
            if len(delta_valores) > 1:
                for account in delta_valores:
                    value = float(account.get('valor').replace('$ ', '').replace(',', ''))
                    mes = account.get('mes')
                    year = account.get('year')

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor': 0}

                    data[year][mes]['valor'] += value


            else:
                if account.data_json != None:
                    data_json = json.loads(account.data_json)
                    value = float(account.valor.amount)
                    mes = data_json['mes'][0]
                    year = data_json['year']

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor': 0}

                    data[year][mes]['valor'] += value

        html = ''

        for year in data.keys():
            html_parte = ''
            for mes in data[year].keys():
                value = '$ {:20,.2f}'.format(data[year][mes]['valor'])
                html_parte += '<li style="list-style-type:initial;"><p><b>{0}: </b>{1}</p></li>'.format(mes, value)

            html += '<div class="row"><div class="col s12"><p><b>Año: </b>{0}</p><div style="margin-left:15px;"><ul>{1}</ul></div></div></div>'.format(
                year, html_parte)

        return html

    def get_context_data(self, **kwargs):

        cut = models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        collect_account = models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        kwargs['title'] = "CUENTA DE COBRO CONTRATO {0}".format(collect_account.contract.nombre)
        kwargs['breadcrum_1'] = cut.consecutive
        kwargs['breadcrum_active'] = collect_account.contract.nombre
        kwargs['valor'] = '$ {:20,.2f}'.format(collect_account.value.amount)
        kwargs['corte'] = '{0}'.format(cut.consecutive)
        kwargs['contratista'] = collect_account.contract.contratista.get_full_name()
        kwargs['contrato'] = collect_account.contract.nombre
        kwargs['cuentas'] = self.get_cuentas_meses()
        kwargs['inicio'] = collect_account.contract.inicio
        kwargs['fin'] = collect_account.contract.fin

        return super(CollectAccountUpdateView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_cut': self.kwargs['pk_cut'],
            'pk_collect_account': self.kwargs['pk_collect_account']
        }
