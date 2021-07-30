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
                        FormView):

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
        consecutivo_cargo = models.Hv.objects.filter(cargo=form.cleaned_data['cargo']).count() + 1
        hv = models.Hv.objects.create(
            contratista = models.Contratistas.objects.get(id = form.cleaned_data['contratista']),
            cargo = form.cleaned_data['cargo'],
            file = form.cleaned_data['file'],
            envio = form.cleaned_data['envio'],
            consecutivo_cargo = consecutivo_cargo,
            region=form.cleaned_data['region'],
            estado='Esperando aprobación',

            numero_tarjeta=form.cleaned_data['numero_tarjeta'],
            fecha_expedicion=form.cleaned_data['fecha_expedicion'],
            folio=form.cleaned_data['folio'],

            titulo_1=form.cleaned_data['titulo_1'],
            institucion_1=form.cleaned_data['institucion_1'],
            nivel_1=form.cleaned_data['nivel_1'],
            grado_1=form.cleaned_data['grado_1'],
            folio_1=form.cleaned_data['folio_1'],

            titulo_2=form.cleaned_data['titulo_2'],
            institucion_2=form.cleaned_data['institucion_2'],
            nivel_2=form.cleaned_data['nivel_2'],
            grado_2=form.cleaned_data['grado_2'],
            folio_2=form.cleaned_data['folio_2'],

            titulo_3=form.cleaned_data['titulo_3'],
            institucion_3=form.cleaned_data['institucion_3'],
            nivel_3=form.cleaned_data['nivel_3'],
            grado_3=form.cleaned_data['grado_3'],
            folio_3=form.cleaned_data['folio_3'],

            titulo_4=form.cleaned_data['titulo_4'],
            institucion_4=form.cleaned_data['institucion_4'],
            nivel_4=form.cleaned_data['nivel_4'],
            grado_4=form.cleaned_data['grado_4'],
            folio_4=form.cleaned_data['folio_4'],

            titulo_5=form.cleaned_data['titulo_5'],
            institucion_5=form.cleaned_data['institucion_5'],
            nivel_5=form.cleaned_data['nivel_5'],
            grado_5=form.cleaned_data['grado_5'],
            folio_5=form.cleaned_data['folio_5'],

            titulo_6=form.cleaned_data['titulo_6'],
            institucion_6=form.cleaned_data['institucion_6'],
            nivel_6=form.cleaned_data['nivel_6'],
            grado_6=form.cleaned_data['grado_6'],
            folio_6=form.cleaned_data['folio_6'],

            titulo_7=form.cleaned_data['titulo_7'],
            institucion_7=form.cleaned_data['institucion_7'],
            nivel_7=form.cleaned_data['nivel_7'],
            grado_7=form.cleaned_data['grado_7'],
            folio_7=form.cleaned_data['folio_7'],

            empresa_1=form.cleaned_data['empresa_1'],
            fecha_inicio_1=form.cleaned_data['fecha_inicio_1'],
            fecha_fin_1=form.cleaned_data['fecha_fin_1'],
            cargo_1=form.cleaned_data['cargo_1'],
            folio_empresa_1=form.cleaned_data['folio_empresa_1'],
            observaciones_1=form.cleaned_data['observaciones_1'],

            empresa_2=form.cleaned_data['empresa_2'],
            fecha_inicio_2=form.cleaned_data['fecha_inicio_2'],
            fecha_fin_2=form.cleaned_data['fecha_fin_2'],
            cargo_2=form.cleaned_data['cargo_2'],
            folio_empresa_2=form.cleaned_data['folio_empresa_2'],
            observaciones_2=form.cleaned_data['observaciones_2'],

            empresa_3=form.cleaned_data['empresa_3'],
            fecha_inicio_3=form.cleaned_data['fecha_inicio_3'],
            fecha_fin_3=form.cleaned_data['fecha_fin_3'],
            cargo_3=form.cleaned_data['cargo_3'],
            folio_empresa_3=form.cleaned_data['folio_empresa_3'],
            observaciones_3=form.cleaned_data['observaciones_3'],

            empresa_4=form.cleaned_data['empresa_4'],
            fecha_inicio_4=form.cleaned_data['fecha_inicio_4'],
            fecha_fin_4=form.cleaned_data['fecha_fin_4'],
            cargo_4=form.cleaned_data['cargo_4'],
            folio_empresa_4=form.cleaned_data['folio_empresa_4'],
            observaciones_4=form.cleaned_data['observaciones_4'],

            empresa_5=form.cleaned_data['empresa_5'],
            fecha_inicio_5=form.cleaned_data['fecha_inicio_5'],
            fecha_fin_5=form.cleaned_data['fecha_fin_5'],
            cargo_5=form.cleaned_data['cargo_5'],
            folio_empresa_5=form.cleaned_data['folio_empresa_5'],
            observaciones_5=form.cleaned_data['observaciones_5'],

            empresa_6=form.cleaned_data['empresa_6'],
            fecha_inicio_6=form.cleaned_data['fecha_inicio_6'],
            fecha_fin_6=form.cleaned_data['fecha_fin_6'],
            cargo_6=form.cleaned_data['cargo_6'],
            folio_empresa_6=form.cleaned_data['folio_empresa_6'],
            observaciones_6=form.cleaned_data['observaciones_6'],

            empresa_7=form.cleaned_data['empresa_7'],
            fecha_inicio_7=form.cleaned_data['fecha_inicio_7'],
            fecha_fin_7=form.cleaned_data['fecha_fin_7'],
            cargo_7=form.cleaned_data['cargo_7'],
            folio_empresa_7=form.cleaned_data['folio_empresa_7'],
            observaciones_7=form.cleaned_data['observaciones_7'],

            empresa_8=form.cleaned_data['empresa_8'],
            fecha_inicio_8=form.cleaned_data['fecha_inicio_8'],
            fecha_fin_8=form.cleaned_data['fecha_fin_8'],
            cargo_8=form.cleaned_data['cargo_8'],
            folio_empresa_8=form.cleaned_data['folio_empresa_8'],
            observaciones_8=form.cleaned_data['observaciones_8'],

            empresa_9=form.cleaned_data['empresa_9'],
            fecha_inicio_9=form.cleaned_data['fecha_inicio_9'],
            fecha_fin_9=form.cleaned_data['fecha_fin_9'],
            cargo_9=form.cleaned_data['cargo_9'],
            folio_empresa_9=form.cleaned_data['folio_empresa_9'],
            observaciones_9=form.cleaned_data['observaciones_9'],

            empresa_10=form.cleaned_data['empresa_10'],
            fecha_inicio_10=form.cleaned_data['fecha_inicio_10'],
            fecha_fin_10=form.cleaned_data['fecha_fin_10'],
            cargo_10=form.cleaned_data['cargo_10'],
            folio_empresa_10=form.cleaned_data['folio_empresa_10'],
            observaciones_10=form.cleaned_data['observaciones_10'],

            empresa_11=form.cleaned_data['empresa_11'],
            fecha_inicio_11=form.cleaned_data['fecha_inicio_11'],
            fecha_fin_11=form.cleaned_data['fecha_fin_11'],
            cargo_11=form.cleaned_data['cargo_11'],
            folio_empresa_11=form.cleaned_data['folio_empresa_11'],
            observaciones_11=form.cleaned_data['observaciones_11']
        )
        trazabilidad = models.TrazabilidadHv.objects.create(
            hv = hv,
            usuario_creacion = self.request.user,
            observacion = 'Carga de la hoja de vida, contratista: {0} - cargo: {1} - región: {2} - envio: Envio {3}'.format(
                str(hv.contratista),
                hv.cargo,
                hv.region,
                hv.envio
            )
        )
        tasks.build_formato_hv(str(hv.id))
        return super(HvCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA HOJA DE VIDA"
        kwargs['url_contratistas'] = '/rest/v1.0/recursos_humanos/hv/autocomplete/contratistas/'
        kwargs['file_url'] = ' N/A'
        return super(HvCreateView,self).get_context_data(**kwargs)



class HvUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):
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
    success_url = "../../"

    def form_valid(self, form):
        hvs = models.Hv.objects.filter(id = self.kwargs['pk'])

        hvs.update(
            contratista=models.Contratistas.objects.get(id=form.cleaned_data['contratista']),
            cargo=form.cleaned_data['cargo'],
            envio=form.cleaned_data['envio'],
            region=form.cleaned_data['region'],
            estado='Esperando aprobación',

            numero_tarjeta=form.cleaned_data['numero_tarjeta'],
            fecha_expedicion=form.cleaned_data['fecha_expedicion'],
            folio=form.cleaned_data['folio'],

            titulo_1=form.cleaned_data['titulo_1'],
            institucion_1=form.cleaned_data['institucion_1'],
            nivel_1=form.cleaned_data['nivel_1'],
            grado_1=form.cleaned_data['grado_1'],
            folio_1=form.cleaned_data['folio_1'],

            titulo_2=form.cleaned_data['titulo_2'],
            institucion_2=form.cleaned_data['institucion_2'],
            nivel_2=form.cleaned_data['nivel_2'],
            grado_2=form.cleaned_data['grado_2'],
            folio_2=form.cleaned_data['folio_2'],

            titulo_3=form.cleaned_data['titulo_3'],
            institucion_3=form.cleaned_data['institucion_3'],
            nivel_3=form.cleaned_data['nivel_3'],
            grado_3=form.cleaned_data['grado_3'],
            folio_3=form.cleaned_data['folio_3'],

            titulo_4=form.cleaned_data['titulo_4'],
            institucion_4=form.cleaned_data['institucion_4'],
            nivel_4=form.cleaned_data['nivel_4'],
            grado_4=form.cleaned_data['grado_4'],
            folio_4=form.cleaned_data['folio_4'],

            titulo_5=form.cleaned_data['titulo_5'],
            institucion_5=form.cleaned_data['institucion_5'],
            nivel_5=form.cleaned_data['nivel_5'],
            grado_5=form.cleaned_data['grado_5'],
            folio_5=form.cleaned_data['folio_5'],

            titulo_6=form.cleaned_data['titulo_6'],
            institucion_6=form.cleaned_data['institucion_6'],
            nivel_6=form.cleaned_data['nivel_6'],
            grado_6=form.cleaned_data['grado_6'],
            folio_6=form.cleaned_data['folio_6'],

            titulo_7=form.cleaned_data['titulo_7'],
            institucion_7=form.cleaned_data['institucion_7'],
            nivel_7=form.cleaned_data['nivel_7'],
            grado_7=form.cleaned_data['grado_7'],
            folio_7=form.cleaned_data['folio_7'],

            empresa_1=form.cleaned_data['empresa_1'],
            fecha_inicio_1=form.cleaned_data['fecha_inicio_1'],
            fecha_fin_1=form.cleaned_data['fecha_fin_1'],
            cargo_1=form.cleaned_data['cargo_1'],
            folio_empresa_1=form.cleaned_data['folio_empresa_1'],
            observaciones_1=form.cleaned_data['observaciones_1'],

            empresa_2=form.cleaned_data['empresa_2'],
            fecha_inicio_2=form.cleaned_data['fecha_inicio_2'],
            fecha_fin_2=form.cleaned_data['fecha_fin_2'],
            cargo_2=form.cleaned_data['cargo_2'],
            folio_empresa_2=form.cleaned_data['folio_empresa_2'],
            observaciones_2=form.cleaned_data['observaciones_2'],

            empresa_3=form.cleaned_data['empresa_3'],
            fecha_inicio_3=form.cleaned_data['fecha_inicio_3'],
            fecha_fin_3=form.cleaned_data['fecha_fin_3'],
            cargo_3=form.cleaned_data['cargo_3'],
            folio_empresa_3=form.cleaned_data['folio_empresa_3'],
            observaciones_3=form.cleaned_data['observaciones_3'],

            empresa_4=form.cleaned_data['empresa_4'],
            fecha_inicio_4=form.cleaned_data['fecha_inicio_4'],
            fecha_fin_4=form.cleaned_data['fecha_fin_4'],
            cargo_4=form.cleaned_data['cargo_4'],
            folio_empresa_4=form.cleaned_data['folio_empresa_4'],
            observaciones_4=form.cleaned_data['observaciones_4'],

            empresa_5=form.cleaned_data['empresa_5'],
            fecha_inicio_5=form.cleaned_data['fecha_inicio_5'],
            fecha_fin_5=form.cleaned_data['fecha_fin_5'],
            cargo_5=form.cleaned_data['cargo_5'],
            folio_empresa_5=form.cleaned_data['folio_empresa_5'],
            observaciones_5=form.cleaned_data['observaciones_5'],

            empresa_6=form.cleaned_data['empresa_6'],
            fecha_inicio_6=form.cleaned_data['fecha_inicio_6'],
            fecha_fin_6=form.cleaned_data['fecha_fin_6'],
            cargo_6=form.cleaned_data['cargo_6'],
            folio_empresa_6=form.cleaned_data['folio_empresa_6'],
            observaciones_6=form.cleaned_data['observaciones_6'],

            empresa_7=form.cleaned_data['empresa_7'],
            fecha_inicio_7=form.cleaned_data['fecha_inicio_7'],
            fecha_fin_7=form.cleaned_data['fecha_fin_7'],
            cargo_7=form.cleaned_data['cargo_7'],
            folio_empresa_7=form.cleaned_data['folio_empresa_7'],
            observaciones_7=form.cleaned_data['observaciones_7'],

            empresa_8=form.cleaned_data['empresa_8'],
            fecha_inicio_8=form.cleaned_data['fecha_inicio_8'],
            fecha_fin_8=form.cleaned_data['fecha_fin_8'],
            cargo_8=form.cleaned_data['cargo_8'],
            folio_empresa_8=form.cleaned_data['folio_empresa_8'],
            observaciones_8=form.cleaned_data['observaciones_8'],

            empresa_9=form.cleaned_data['empresa_9'],
            fecha_inicio_9=form.cleaned_data['fecha_inicio_9'],
            fecha_fin_9=form.cleaned_data['fecha_fin_9'],
            cargo_9=form.cleaned_data['cargo_9'],
            folio_empresa_9=form.cleaned_data['folio_empresa_9'],
            observaciones_9=form.cleaned_data['observaciones_9'],

            empresa_10=form.cleaned_data['empresa_10'],
            fecha_inicio_10=form.cleaned_data['fecha_inicio_10'],
            fecha_fin_10=form.cleaned_data['fecha_fin_10'],
            cargo_10=form.cleaned_data['cargo_10'],
            folio_empresa_10=form.cleaned_data['folio_empresa_10'],
            observaciones_10=form.cleaned_data['observaciones_10'],

            empresa_11=form.cleaned_data['empresa_11'],
            fecha_inicio_11=form.cleaned_data['fecha_inicio_11'],
            fecha_fin_11=form.cleaned_data['fecha_fin_11'],
            cargo_11=form.cleaned_data['cargo_11'],
            folio_empresa_11=form.cleaned_data['folio_empresa_11'],
            observaciones_11=form.cleaned_data['observaciones_11']
        )

        hv = models.Hv.objects.get(id=self.kwargs['pk'])
        hv.file = form.cleaned_data['file']
        hv.save()
        trazabilidad = models.TrazabilidadHv.objects.create(
            hv=hv,
            usuario_creacion=self.request.user,
            observacion='Actualización de la hoja de vida, contratista: {0} - cargo: {1} - región: {2} - envio: Envio {3}'.format(
                str(hv.contratista),
                hv.cargo,
                hv.region,
                hv.envio
            )
        )
        tasks.build_formato_hv(str(hv.id))

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