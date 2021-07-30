from django.apps import AppConfig


class ReportesConfig(AppConfig):
    name = 'reportes'

    def ready(self):
        self.sican_name = "Reportes"
        self.sican_icon = "save"
        self.sican_description = "Consulta y descarga de los reportes generados por el sistema"
        self.sican_color = "brown darken-3"
        self.sican_url = '/reportes/'
        self.sican_categoria = 'sion'
        self.sican_order = 4
        self.sican_permiso = 'usuarios.reportes.ver'