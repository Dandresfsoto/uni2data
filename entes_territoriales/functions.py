from entes_territoriales import models
from django.utils import timezone

def delta_contacto(contacto):

    ret = {
            'ops':[
                {
                    'attributes': {'bold':True, 'header': 3},
                    'insert': 'CONTACTO'
                },
                {
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Nombre: '
                },
                {
                    'insert': contacto.nombres,
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Cargo: '
                },
                {
                    'insert': contacto.cargo,
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Celular: '
                },
                {
                    'insert': str(contacto.celular),
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Email: '
                },
                {
                    'insert': contacto.email,
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Observaciones: '
                },
                {
                    'insert': contacto.observaciones,
                }
            ]
        }

    return ret

def delta_estado(hito):

    ret = {
            'ops':[
                {
                    'attributes': {'bold':True, 'header': 3},
                    'insert': 'Actualización de estado'
                },
                {
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Estado: '
                },
                {
                    'insert': hito.estado,
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'Observacion: '
                },
                {
                    'insert': hito.observacion,
                },
                {
                    'insert': '\n'
                },
            ]
        }

    return ret

def delta_empty():

    ret = {
            'ops':[

                {
                    'insert': '\n'
                },
            ]
        }

    return ret