from django.apps import AppConfig

class Fest2020_Config(AppConfig):
    name = 'fest_2020_'

    def ready(self):
        self.sican_name = "IRACA"
        self.sican_icon = "accessibility"
        self.sican_description = "Proyecto IRACA"
        self.sican_color = "blue darken-4"
        self.sican_url = '/iraca_2021/'
        self.sican_categoria = 'IRACA'
        self.sican_order = 10
        self.sican_permiso = 'usuarios.iraca_2021.ver'
