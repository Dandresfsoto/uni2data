from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from desplazamiento import forms, models
from django.http import HttpResponseRedirect
from django.utils import timezone

# Create your views here.
#----------------------------------- DESPLAZAMIENTOS -------------------------------------

class SolicitudesDesplazamientoView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOLICITUDES DE DESPLAZAMIENTO"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/solicitudes_desplazamiento/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.crear')
        return super(SolicitudesDesplazamientoView,self).get_context_data(**kwargs)


class SolicitudesDesplazamientoCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/crear.html'
    form_class = forms.SolicitudesForm
    success_url = "../"
    model = models.Solicitudes

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Solicitudes.objects.filter(usuario_creacion = self.request.user).count() + 1
        self.object.usuario_creacion = self.request.user
        self.object.valor = 0
        self.object.estado = ''
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA SOLICITUD"
        return super(SolicitudesDesplazamientoCreateView,self).get_context_data(**kwargs)


class SolicitudesDesplazamientoUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/editar.html'
    form_class = forms.SolicitudesUpdateForm
    success_url = "../../"
    model = models.Solicitudes

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Solicitud completa'
        self.object.actualizacion = timezone.now()
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR SOLICITUD"
        kwargs['breadcrum_active'] = models.Solicitudes.objects.get(id = self.kwargs['pk']).nombre
        kwargs['formato_firmado'] = models.Solicitudes.objects.get(id = self.kwargs['pk']).pretty_print_url_file2()
        return super(SolicitudesDesplazamientoUpdateView,self).get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):

        solicitud = models.Solicitudes.objects.get(id = self.kwargs['pk'])

        if request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.ver') and solicitud.estado == 'Aprobado' and solicitud.file2 == '':

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)


        else:
            return HttpResponseRedirect(redirect('../../'))



class ListaDesplazamientosView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/desplazamientos/lista.html'


    def get_context_data(self, **kwargs):
        solicitud = models.Solicitudes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "DESPLAZAMIENTOS"
        kwargs['breadcrum_active'] = solicitud.nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/solicitudes_desplazamiento/desplazamientos/{0}'.format(self.kwargs['pk'])
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.crear') and solicitud.estado == ''
        return super(ListaDesplazamientosView,self).get_context_data(**kwargs)


class DesplazamientosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/desplazamientos/crear.html'
    form_class = forms.DesplazamientoForm
    success_url = "../"
    model = models.Desplazamiento

    def dispatch(self, request, *args, **kwargs):

        solicitud = models.Solicitudes.objects.get(id = self.kwargs['pk'])

        if request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.ver') and solicitud.estado == '':

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('../')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.solicitud = models.Solicitudes.objects.get(id = self.kwargs['pk'])
        self.object.valor = float(form.cleaned_data['valor'].replace('$ ','').replace(',',''))
        self.object.valor_original = float(form.cleaned_data['valor'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(DesplazamientosCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        solicitud = models.Solicitudes.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVO DESPLAZAMIENTO"
        kwargs['breadcrum_active'] = solicitud.nombre
        return super(DesplazamientosCreateView,self).get_context_data(**kwargs)


class DesplazamientosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/solicitudes_desplazamiento/desplazamientos/editar.html'
    form_class = forms.DesplazamientoForm
    success_url = "../../"
    model = models.Desplazamiento
    pk_url_kwarg = 'pk_desplazamiento'


    def dispatch(self, request, *args, **kwargs):

        solicitud = models.Solicitudes.objects.get(id = self.kwargs['pk'])

        if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.editar') and solicitud.estado == '':

            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.valor = float(form.cleaned_data['valor'].replace('$ ','').replace(',',''))
        self.object.valor_original = float(form.cleaned_data['valor'].replace('$ ', '').replace(',', ''))
        self.object.save()
        return super(DesplazamientosUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        solicitud = models.Solicitudes.objects.get(id=self.kwargs['pk'])
        desplazamiento = models.Desplazamiento.objects.get(id=self.kwargs['pk_desplazamiento'])
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
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.ver",
            "usuarios.cpe_2018.solicitudes_desplazamiento.eliminar",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"


    def dispatch(self, request, *args, **kwargs):
        solicitud = models.Solicitudes.objects.get(id = self.kwargs['pk'])

        if request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.editar') and solicitud.estado == '':
            desplazamiento = models.Desplazamiento.objects.get(id = self.kwargs['pk_desplazamiento'])
            if desplazamiento.estado == None:
                desplazamiento.delete()

        return HttpResponseRedirect('../../')
#----------------------------------------------------------------------------------