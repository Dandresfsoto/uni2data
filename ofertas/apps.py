from django.apps import AppConfig


class OfertasConfig(AppConfig):
    name = 'ofertas'

    def ready(self):
        self.sican_name = "Ofertas de empleo"
        self.sican_icon = "hourglass_empty"
        self.sican_description = "Recolección de información y soportes para vacantes en la asociación"
        self.sican_color = "pink darken-4"
        self.sican_url = '/ofertas/'
        self.sican_categoria = 'sion'
        self.sican_order = 8
        self.sican_permiso = 'usuarios.ofertas.ver'
        self.sican_publico = True
