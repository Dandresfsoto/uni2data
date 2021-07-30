import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import models as rh_models
from mis_contratos import forms
from django.http import HttpResponseRedirect
# Create your views here.

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