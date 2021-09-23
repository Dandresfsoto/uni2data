from django.apps import AppConfig


class IracaConfig(AppConfig):
    name = 'iraca'

    def ready(self):
        self.sican_name = "IRACA"
        self.sican_icon = "group"
        self.sican_description = "Proyecto IRACA"
        self.sican_color = "#673ab7 deep-purple"
        self.sican_url = '/iraca_new/'
        self.sican_categoria = 'Iraca'
        self.sican_order = 11
        self.sican_permiso = 'usuarios.iraca.ver'

