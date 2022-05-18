from django.apps import AppConfig


class InventarioConfig(AppConfig):
    name = 'inventario'

    def ready(self):
        self.sican_name = "Inventario"
        self.sican_icon = "assignment"
        self.sican_description = "Inventario y despacho"
        self.sican_color = "#ad1457 pink darken-3"
        self.sican_url = '/inventario/'
        self.sican_categoria = 'Inventario'
        self.sican_order = 13
        self.sican_permiso = 'usuarios.inventario.ver'