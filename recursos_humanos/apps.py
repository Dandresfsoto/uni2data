from django.apps import AppConfig


class RecursosHumanosConfig(AppConfig):
    name = 'recursos_humanos'

    def ready(self):
        self.sican_name = "Gestión Humana"
        self.sican_icon = "directions_run"
        self.sican_description = "Gestión de personal"
        self.sican_color = "red darken-3"
        self.sican_url = '/recursos_humanos/'
        self.sican_categoria = 'direccion'
        self.sican_order = 4
        self.sican_permiso = 'usuarios.recursos_humanos.ver'