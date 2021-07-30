from recursos_humanos.models import Contratos
from django.utils import timezone

def certificacion_laboral(contratista):

    contratos = []

    contratos_obj = Contratos.objects.filter(contratista=contratista)

    if contratos_obj.count() > 0:
        for contrato in contratos_obj:
            contratos.append({
                'attributes': {'bold': True},
                'insert': 'CONTRATO {0} N° {1}: '.format(contrato.tipo_contrato.upper(),contrato.nombre.upper())
            })
            contratos.append({
                'insert': '{0} - {1}'.format(contrato.pretty_print_inicio(),contrato.pretty_print_fin())
            })
            contratos.append({
                'attributes': {'align': 'justify'},
                'insert': '\n'
            })
            contratos.append({
                'attributes': {'bold': True},
                'insert': 'Objeto: '
            })
            contratos.append({
                'insert': contrato.objeto_contrato
            })
            contratos.append({
                'attributes': {'align': 'justify'},
                'insert': '\n'
            })
            contratos.append({
                'insert': '\n'
            })
    else:
        contratos.append(
            {
                'attributes': {'bold': True},
                'insert': 'No hay contratos registrados.'
            }
        )
        contratos.append(
            {
                'attributes': {'align': 'justify'},
                'insert': '\n'
            }
        )
        contratos.append({
            'insert': '\n'
        })

    ret = {
            'ops':[
                {
                    'attributes': {'bold':True},
                    'insert': 'LA ASOCIACIÓN NACIONAL PARA EL DESARROLLO SOCIAL ANDES'
                },
                {
                    'attributes': {'align': 'center','header':3},
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'NIT. 800.228.885-3'
                },
                {
                    'attributes': {'align': 'center', 'header': 3},
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                },
                {
                    'attributes': {'bold': True},
                    'insert': 'CERTIFICA:'
                },
                {
                    'attributes': {'align': 'center', 'header': 3},
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                },
                {
                    'insert': 'Que en el sistema de información SICAN se encuentra registrada la siguiente información de '
                },
                {
                    'attributes': {'bold': True},
                    'insert': contratista.fullname()
                },
                {
                    'insert': ', identificado(a) con cédula de ciudadanía N° '
                },
                {
                    'attributes': {'bold': True},
                    'insert': str(contratista.cedula)
                },
                {
                    'insert': ':'
                },
                {
                    'attributes': {'align': 'justify'},
                    'insert': '\n'
                },
                {
                    'insert': '\n'
                }
            ] + contratos +
            [
                {
                    'insert': 'La presente se expide a solicitud del interesado a los {}'.format(timezone.now().strftime('%d días del mes de %B del %Y.'))
                },
                {
                    'attributes': {'align': 'justify'},
                    'insert': '\n'
                },
            ]
        }

    return ret