from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from formatos import forms, models
from django.http import HttpResponseRedirect
from django.utils import timezone

# Create your views here.
#--------------------------------------- LEVEL 1 ----------------------------------------

class ComponentesView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        return super(ComponentesView,self).get_context_data(**kwargs)


class ComponentesLevel1CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/crear.html'
    form_class = forms.Level1Form
    success_url = "../"
    model = models.Level1

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level1.objects.all().count() + 1
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        return super(ComponentesLevel1CreateView,self).get_context_data(**kwargs)

class ComponentesLevel1UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/editar.html'
    form_class = forms.Level1Form
    success_url = "../../"
    model = models.Level1


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level1.pretty_print_url_file()
        kwargs['breadcrum_active'] = level1.nombre
        return super(ComponentesLevel1UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 2 ----------------------------------------

class ComponentesLevel2View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level2/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/'.format(level1.id)
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_active'] = level1.nombre
        return super(ComponentesLevel2View,self).get_context_data(**kwargs)


class ComponentesLevel2CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level2/crear.html'
    form_class = forms.Level2Form
    success_url = "../"
    model = models.Level2

    def form_valid(self, form):
        level = models.Level1.objects.get(id=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level2.objects.filter(level__id = self.kwargs['pk']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_active'] = level1.nombre
        return super(ComponentesLevel2CreateView,self).get_context_data(**kwargs)

class ComponentesLevel2UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level2/editar.html'
    form_class = forms.Level2Form
    success_url = "../../"
    model = models.Level2
    pk_url_kwarg = 'pk_l2'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level2.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_active'] = level2.nombre
        return super(ComponentesLevel2UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 3 ----------------------------------------

class ComponentesLevel3View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level3/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/'.format(
            level1.id,
            level2.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_active'] = level2.nombre
        return super(ComponentesLevel3View,self).get_context_data(**kwargs)


class ComponentesLevel3CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level3/crear.html'
    form_class = forms.Level3Form
    success_url = "../"
    model = models.Level3

    def form_valid(self, form):
        level = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level3.objects.filter(level__id=self.kwargs['pk_l2']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_active'] = level2.nombre
        return super(ComponentesLevel3CreateView,self).get_context_data(**kwargs)

class ComponentesLevel3UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level3/editar.html'
    form_class = forms.Level3Form
    success_url = "../../"
    model = models.Level3
    pk_url_kwarg = 'pk_l3'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level3.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_active'] = level3.nombre
        return super(ComponentesLevel3UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 4 ----------------------------------------

class ComponentesLevel4View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level4/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/{2}/'.format(
            level1.id,
            level2.id,
            level3.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_active'] = level3.nombre
        return super(ComponentesLevel4View,self).get_context_data(**kwargs)


class ComponentesLevel4CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level4/crear.html'
    form_class = forms.Level4Form
    success_url = "../"
    model = models.Level4

    def form_valid(self, form):
        level = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level4.objects.filter(level__id=self.kwargs['pk_l3']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_active'] = level3.nombre
        return super(ComponentesLevel4CreateView,self).get_context_data(**kwargs)

class ComponentesLevel4UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level4/editar.html'
    form_class = forms.Level4Form
    success_url = "../../"
    model = models.Level4
    pk_url_kwarg = 'pk_l4'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level4.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_active'] = level4.nombre
        return super(ComponentesLevel4UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 5 ----------------------------------------

class ComponentesLevel5View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level5/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/{2}/{3}/'.format(
            level1.id,
            level2.id,
            level3.id,
            level4.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_active'] = level4.nombre
        return super(ComponentesLevel5View,self).get_context_data(**kwargs)


class ComponentesLevel5CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level5/crear.html'
    form_class = forms.Level5Form
    success_url = "../"
    model = models.Level5

    def form_valid(self, form):
        level = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level5.objects.filter(level__id=self.kwargs['pk_l4']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_active'] = level4.nombre
        return super(ComponentesLevel5CreateView,self).get_context_data(**kwargs)

class ComponentesLevel5UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level5/editar.html'
    form_class = forms.Level5Form
    success_url = "../../"
    model = models.Level5
    pk_url_kwarg = 'pk_l5'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level5.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_active'] = level5.nombre
        return super(ComponentesLevel5UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 6 ----------------------------------------

class ComponentesLevel6View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level6/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/{2}/{3}/{4}/'.format(
            level1.id,
            level2.id,
            level3.id,
            level4.id,
            level5.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_active'] = level5.nombre
        return super(ComponentesLevel6View,self).get_context_data(**kwargs)


class ComponentesLevel6CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level6/crear.html'
    form_class = forms.Level6Form
    success_url = "../"
    model = models.Level6

    def form_valid(self, form):
        level = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level6.objects.filter(level__id=self.kwargs['pk_l5']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_active'] = level5.nombre
        return super(ComponentesLevel6CreateView,self).get_context_data(**kwargs)

class ComponentesLevel6UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level6/editar.html'
    form_class = forms.Level6Form
    success_url = "../../"
    model = models.Level6
    pk_url_kwarg = 'pk_l6'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level6.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_active'] = level6.nombre
        return super(ComponentesLevel6UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 7 ----------------------------------------

class ComponentesLevel7View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level7/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/{2}/{3}/{4}/{5}/'.format(
            level1.id,
            level2.id,
            level3.id,
            level4.id,
            level5.id,
            level6.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_active'] = level6.nombre
        return super(ComponentesLevel7View,self).get_context_data(**kwargs)


class ComponentesLevel7CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level7/crear.html'
    form_class = forms.Level7Form
    success_url = "../"
    model = models.Level7

    def form_valid(self, form):
        level = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level7.objects.filter(level__id=self.kwargs['pk_l6']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_active'] = level6.nombre
        return super(ComponentesLevel7CreateView,self).get_context_data(**kwargs)

class ComponentesLevel7UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level7/editar.html'
    form_class = forms.Level7Form
    success_url = "../../"
    model = models.Level7
    pk_url_kwarg = 'pk_l7'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        level7 = models.Level7.objects.get(id=self.kwargs['pk_l7'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level7.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_6'] = level6.nombre
        kwargs['breadcrum_active'] = level7.nombre
        return super(ComponentesLevel7UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------

#--------------------------------------- LEVEL 8 ----------------------------------------

class ComponentesLevel8View(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level8/lista.html'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        level7 = models.Level7.objects.get(id=self.kwargs['pk_l7'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formatos/{0}/{1}/{2}/{3}/{4}/{5}/{6}/'.format(
            level1.id,
            level2.id,
            level3.id,
            level4.id,
            level5.id,
            level6.id,
            level7.id
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formatos.crear')
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_6'] = level6.nombre
        kwargs['breadcrum_active'] = level7.nombre
        return super(ComponentesLevel8View,self).get_context_data(**kwargs)


class ComponentesLevel8CreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level8/crear.html'
    form_class = forms.Level8Form
    success_url = "../"
    model = models.Level8

    def form_valid(self, form):
        level = models.Level7.objects.get(id=self.kwargs['pk_l7'])
        self.object = form.save(commit=False)
        self.object.consecutivo = models.Level8.objects.filter(level__id=self.kwargs['pk_l7']).count() + 1
        self.object.level = level
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id=self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        level7 = models.Level7.objects.get(id=self.kwargs['pk_l7'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_6'] = level6.nombre
        kwargs['breadcrum_active'] = level7.nombre
        return super(ComponentesLevel8CreateView,self).get_context_data(**kwargs)

class ComponentesLevel8UpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formatos.ver",
            "usuarios.cpe_2018.formatos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formatos/level8/editar.html'
    form_class = forms.Level8Form
    success_url = "../../"
    model = models.Level8
    pk_url_kwarg = 'pk_l8'


    def get_context_data(self, **kwargs):
        level1 = models.Level1.objects.get(id = self.kwargs['pk'])
        level2 = models.Level2.objects.get(id=self.kwargs['pk_l2'])
        level3 = models.Level3.objects.get(id=self.kwargs['pk_l3'])
        level4 = models.Level4.objects.get(id=self.kwargs['pk_l4'])
        level5 = models.Level5.objects.get(id=self.kwargs['pk_l5'])
        level6 = models.Level6.objects.get(id=self.kwargs['pk_l6'])
        level7 = models.Level7.objects.get(id=self.kwargs['pk_l7'])
        level8 = models.Level8.objects.get(id=self.kwargs['pk_l8'])
        kwargs['title'] = "FORMATOS"
        kwargs['url_file'] = level8.pretty_print_url_file()
        kwargs['breadcrum_1'] = level1.nombre
        kwargs['breadcrum_2'] = level2.nombre
        kwargs['breadcrum_3'] = level3.nombre
        kwargs['breadcrum_4'] = level4.nombre
        kwargs['breadcrum_5'] = level5.nombre
        kwargs['breadcrum_6'] = level6.nombre
        kwargs['breadcrum_7'] = level7.nombre
        kwargs['breadcrum_active'] = level8.nombre
        return super(ComponentesLevel8UpdateView,self).get_context_data(**kwargs)

#-----------------------------------------------------------------------------------------