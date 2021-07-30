from django.apps import AppConfig


class UsuariosConfig(AppConfig):

    name = 'usuarios'

    def ready(self):
        self.sican_name = "Usuarios"
        self.sican_icon = "account_circle"
        self.sican_description = "Cuentas, roles y permisos"
        self.sican_color = "orange darken-3"
        self.sican_url = '/usuarios/'
        self.sican_categoria = 'sion'
        self.sican_order = 5
        self.sican_permiso = 'usuarios.usuarios.ver'