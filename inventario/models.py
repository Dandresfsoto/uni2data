import uuid

from django.db import models
from djmoney.models.fields import MoneyField


class Productos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.CharField(max_length=150, verbose_name='Codigo')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')
    stock = models.IntegerField(default=0, verbose_name='Cantidad')


    def __str__(self):
        return self.nombre

    def pretty_print_precio(self):
        precio = self.valor
        return str(precio).replace('COL','')