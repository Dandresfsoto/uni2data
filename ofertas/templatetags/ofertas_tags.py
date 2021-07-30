from django import template

register = template.Library()

@register.filter
def oferta_aplicacion(user,oferta):
    return oferta.get_aplicacion(user)