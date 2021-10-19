from delta import html
import json
import mimetypes
from bs4 import BeautifulSoup
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import models as rh_models
from mis_contratos import forms
from django.http import HttpResponseRedirect
from django.utils import timezone
import io
from django.core.files import File
import pdfkit

#------------------------------- SELECCIÓN ----------------------------------------

class ContratosListView(LoginRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'mis_contratos/lista.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = "MIS CONTRATOS"
        kwargs['url_datatable'] = '/rest/v1.0/mis_contratos/'
        return super(ContratosListView,self).get_context_data(**kwargs)


class ContratosSoportesListView(LoginRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'mis_contratos/lista_soportes.html'


    def get_context_data(self, **kwargs):
        contrato = rh_models.Contratos.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "SOPORTES DE CONTRATO"
        kwargs['url_datatable'] = '/rest/v1.0/mis_contratos/soportes/{0}/'.format(str(self.kwargs['pk']))
        kwargs['breadcrum_active'] = contrato.nombre
        return super(ContratosSoportesListView,self).get_context_data(**kwargs)


class ContratosSoportesUpdateView(LoginRequiredMixin,
                        UpdateView):
    login_url = settings.LOGIN_URL
    template_name = 'mis_contratos/subir_soporte.html'
    form_class = forms.SoportesContratosForm
    success_url = "../../"
    model = rh_models.SoportesContratos
    pk_url_kwarg = 'pk_soporte_contrato'


    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id = self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())


    def form_valid(self, form):
        self.object = form.save()

        if self.object.estado == 'Solicitar subsanación' and self.request.user == self.object.contrato.contratista.usuario_asociado:
            self.object.estado = ''
            self.object.observacion = ''
            self.object.save()

        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        soporte = rh_models.SoportesContratos.objects.get(id = self.kwargs['pk_soporte_contrato'])
        kwargs['title'] = "CARGAR SOPORTE DE CONTRATO"
        kwargs['breadcrum_active'] = rh_models.Contratos.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = soporte.soporte.nombre
        kwargs['soporte_url'] = soporte.pretty_print_url_file()
        kwargs['nombre_soporte'] = str(soporte.soporte)

        return super(ContratosSoportesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_soporte': self.kwargs['pk'],
        }

#----------------------------------------------------------------------------------

#--------------------------------CUENTAS DE COBRO----------------------------------


class ContractsAccountsListView(LoginRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'mis_contratos/accounts/list.html'


    def get_context_data(self, **kwargs):
        contract = rh_models.Contratos.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "CUENTAS DE COBRO DEL CONTRATO {0}".format(contract.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/mis_contratos/accounts/{0}/'.format(str(self.kwargs['pk']))
        kwargs['breadcrum_active'] = contract.nombre
        return super(ContractsAccountsListView,self).get_context_data(**kwargs)

class ContractsAccountsSegurityUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'mis_contratos/accounts/upload.html'
    form_class = forms.SegurityUploadForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id=self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super(ContractsAccountsSegurityUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])
        kwargs['title'] = "CARGAR SEGURIDAD SOCIAL"
        kwargs['breadcrum_1'] = collec_account.cut.consecutive
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        kwargs['file5_url'] = collec_account.pretty_print_url_file5()
        return super(ContractsAccountsSegurityUploadView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk'],
                'pk_accounts':self.kwargs['pk_accounts']}

class ContractsAccountsAccountUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'mis_contratos/accounts/upload.html'
    form_class = forms.AccountUploadForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id=self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super(ContractsAccountsAccountUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])
        kwargs['title'] = "CARGAR CUENTA DE COBRO"
        kwargs['breadcrum_1'] = collec_account.cut.consecutive
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        kwargs['file3_url'] = collec_account.pretty_print_url_file3()
        kwargs['file4_url'] = collec_account.pretty_print_url_file4()
        return super(ContractsAccountsAccountUploadView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk'],
                'pk_accounts':self.kwargs['pk_accounts']}

class ContractsAccountsActivityUploadView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'mis_contratos/accounts/activity.html'
    form_class = forms.AccountActivityForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id=self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):

        day = timezone.now()
        date = day.strftime("%Y/%m/%d")
        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])

        collect_account.delta = form.cleaned_data['contenido']
        collect_account.save()
        delta = json.loads(form.cleaned_data['contenido'])

        delta_2 = BeautifulSoup(html.render(delta['ops']),"html.parser",from_encoding='utf-8')

        collect_account.file6.delete()

        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])

        template_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/informe_actividades/inform.html', 'rb'), "html.parser")

        template_header_tag = template_header.find(class_='codigo_span')
        template_header_tag.insert(1, str(collect_account.id))

        template_header_tag = template_header.find(class_='date_span')
        template_header_tag.insert(1, str(date))

        template_header_tag = template_header.find(class_='charge_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.cargo))

        template_header_tag = template_header.find(class_='name_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))

        template_header_tag = template_header.find(class_='month_span')
        template_header_tag.insert(1, str(collect_account.month))

        template_header_tag = template_header.find(class_='name_span_1')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='content_span_1')
        template_header_tag.insert(1, delta_2)

        template_header_tag = template_header.find(class_='name_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))

        collect_account.html_3.save('informe_actividades.html',
                                    File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        collect_account.file6.save('informe_actividades.pdf',
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

        pdfkit.from_file([collect_account.html_3.path], collect_account.file6.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\informe_actividades\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\informe_actividades\\footer\\footer.html',
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '4cm',
            'margin-bottom': '3cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }, configuration=config)


        return super(ContractsAccountsActivityUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])
        kwargs['title'] = "CREAR INFORME DE ACTIVIDADES"
        kwargs['breadcrum_1'] = collec_account.cut.consecutive
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        return super(ContractsAccountsActivityUploadView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk'],
                'pk_accounts':self.kwargs['pk_accounts']}

class ContractsAccountsActivityUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'mis_contratos/accounts/activity_update.html'
    form_class = forms.AccountUpdateActivityForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id=self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):

        day = timezone.now()
        date = day.strftime("%Y/%m/%d")
        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])

        collect_account.delta = form.cleaned_data['contenido']
        collect_account.save()
        delta = json.loads(form.cleaned_data['contenido'])

        delta_2 = BeautifulSoup(html.render(delta['ops']),"html.parser",from_encoding='utf-8')

        collect_account.file6.delete()

        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])

        template_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/informe_actividades/inform.html', 'rb'), "html.parser")

        template_header_tag = template_header.find(class_='codigo_span')
        template_header_tag.insert(1, str(collect_account.id))

        template_header_tag = template_header.find(class_='date_span')
        template_header_tag.insert(1, str(date))

        template_header_tag = template_header.find(class_='charge_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.cargo))

        template_header_tag = template_header.find(class_='name_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))

        template_header_tag = template_header.find(class_='month_span')
        template_header_tag.insert(1, str(collect_account.month))

        template_header_tag = template_header.find(class_='name_span_1')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='content_span_1')
        template_header_tag.insert(1, delta_2)

        template_header_tag = template_header.find(class_='name_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))

        collect_account.html_3.save('informe_actividades.html',
                                    File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        collect_account.file6.save('informe_actividades.pdf',
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

        pdfkit.from_file([collect_account.html_3.path], collect_account.file6.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\informe_actividades\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\informe_actividades\\footer\\footer.html',
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '4cm',
            'margin-bottom': '3cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }, configuration=config)


        return super(ContractsAccountsActivityUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])
        kwargs['title'] = "CREAR INFORME DE ACTIVIDADES"
        kwargs['breadcrum_1'] = collec_account.cut.consecutive
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        return super(ContractsAccountsActivityUpdateView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk'],
                'pk_accounts':self.kwargs['pk_accounts']}

class ContractsAccountsAccountUploadInformView(UpdateView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'mis_contratos/accounts/upload_inform.html'
    form_class = forms.AccountUploadInformForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    def dispatch(self, request, *args, **kwargs):

        contrato = rh_models.Contratos.objects.get(id=self.kwargs['pk'])

        if contrato.contratista.usuario_asociado == self.request.user:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super(ContractsAccountsAccountUploadInformView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_accounts'])
        kwargs['title'] = "CARGAR INFORME DE ACTIVIDADES"
        kwargs['breadcrum_1'] = collec_account.cut.consecutive
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        kwargs['file4_url'] = collec_account.pretty_print_url_file4()
        return super(ContractsAccountsAccountUploadInformView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk'],
                'pk_accounts':self.kwargs['pk_accounts']}
