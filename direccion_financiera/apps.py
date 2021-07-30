from django.apps import AppConfig


class DireccionFinancieraConfig(AppConfig):
    name = 'direccion_financiera'

    def ready(self):
        self.sican_name = "Dirección financiera"
        self.sican_icon = "monetization_on"
        self.sican_description = "Reportes de pago e información contable"
        self.sican_color = "teal darken-3"
        self.sican_url = '/direccion_financiera/'
        self.sican_categoria = 'financiera'
        self.sican_order = 5
        self.sican_permiso = 'usuarios.direccion_financiera.ver'