from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View


#------------------------------- SELECTION ----------------------------------------
from iraca import forms, models
from iraca.models import Certificates
from usuarios.models import Municipios


class IracaOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/list.html'
    permissions = {
        "all": [
            "usuarios.iraca.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(IracaOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.iraca.actas.ver'):
            items.append({
                'sican_categoria': 'Actas',
                'sican_color': 'brown darken-4',
                'sican_order': 1,
                'sican_url': 'certificate/',
                'sican_name': 'Actas',
                'sican_icon': 'assignment',
                'sican_description': 'Actas diligenciadas para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.socializacion.ver'):
            items.append({
                'sican_categoria': 'Socializacion y concertacion',
                'sican_color': 'green darken-4',
                'sican_order': 2,
                'sican_url': 'socialization/',
                'sican_name': 'Socializacion',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Actas de socializacion y concertacion para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.vinculacion.ver'):
            items.append({
                'sican_categoria': 'Vinculacion y caracterizacion',
                'sican_color': 'blue darken-4',
                'sican_order': 3,
                'sican_url': 'bonding/',
                'sican_name': 'Vinculacion',
                'sican_icon': 'people',
                'sican_description': 'Informacion de Vinculacion y caracterizacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.formulacion.ver'):
            items.append({
                'sican_categoria': 'Formulacion y convalidacion',
                'sican_color': 'orange darken-4',
                'sican_order': 4,
                'sican_url': 'formulation/',
                'sican_name': 'Formulacion',
                'sican_icon': 'pie_chart',
                'sican_description': 'Informacion de Formulacion y convalidacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.implementacion.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 5,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'work',
                'sican_description': 'Informacion de implementacion del proyecto Iraca 2021'
            })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "IRACA"
        kwargs['items'] = self.get_items()
        return super(IracaOptionsView,self).get_context_data(**kwargs)



#----------------------------------------------------------------------------------

#------------------------------- CERTIFICATES -------------------------------------


class CerticateOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/list.html'

    def get_items(self):
        items = []

        for certificate in Certificates.objects.all().order_by('code'):
            if self.request.user.has_perm('usuarios.certificate.ver'):
                items.append({
                    'sican_categoria': '{0}'.format(certificate.name),
                    'sican_color': certificate.color,
                    'sican_order': certificate.code,
                    'sican_url': '{0}/'.format(str(certificate.id)),
                    'sican_name': '{0}'.format(certificate.name),
                    'sican_description': 'Actas de {0}.'.format(certificate.name).lower()
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.actas.ver",
            ]
        }

        items = self.get_items()
        if len(items) == 0:
            return HttpResponseRedirect('../')

        else:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(self.login_url)
            else:
                if request.user.has_perms(self.permissions.get('all')):
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTAS"
        kwargs['items'] = self.get_items()
        return super(CerticateOptionsView,self).get_context_data(**kwargs)



#----------------------------------------------------------------------------------

#------------------------------- MEEETINGS -------------------------------------


class CerticateListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/municipalities.html'


    def get_context_data(self, **kwargs):
        certificate = Certificates.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = str(certificate.name).upper()
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/'.format(certificate.id)
        kwargs['breadcrum_1'] = certificate.name
        return super(CerticateListView,self).get_context_data(**kwargs)


class CerticateCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.crear",

        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/create.html'
    form_class = forms.CertificateForm
    success_url = "../"

    def form_valid(self, form):
        certificate = Certificates.objects.get(id=self.kwargs['pk'])
        municipality = Municipios.objects.get(id = str(form.cleaned_data['municipality']))

        models.Meetings.objects.create(
            creation_user = self.request.user,
            user_update = self.request.user,
            municipality = municipality,
            certificate = certificate
        )

        #self.object = form.save(commit=False)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        certificate = Certificates.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVA GESTIÓN"
        kwargs['breadcrum_1'] = certificate.name
        kwargs['url_autocomplete_municipality'] = '/rest/v1.0/iraca_new/certificate/autocomplete/municipios/'
        return super(CerticateCreateView,self).get_context_data(**kwargs)

