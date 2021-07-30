from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
# Create your views here.


#------------------------------------ REPORTES --------------------------------------

class ReportesView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.reportes.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'reportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "reportes"
        kwargs['url_datatable'] = '/rest/v1.0/reportes/'
        return super(ReportesView,self).get_context_data(**kwargs)

#------------------------------------------------------------------------------------