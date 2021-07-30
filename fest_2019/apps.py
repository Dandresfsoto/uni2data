from django.apps import AppConfig

class Fest2019Config(AppConfig):
    name = 'fest_2019'

    def ready(self):
        self.sican_name = "IRACA"
        self.sican_icon = "accessibility"
        self.sican_description = "Proyecto IRACA intervención 2019 - 2020"
        self.sican_color = "grey darken-4"
        self.sican_url = '/iraca/'
        self.sican_categoria = 'Iraca'
        self.sican_order = 10
        self.sican_permiso = 'usuarios.fest_2019.ver'
