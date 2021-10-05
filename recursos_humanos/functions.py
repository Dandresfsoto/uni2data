import json

from num2words import num2words

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

def cuenta_cobro(collect_account):

    expedicion = ''
    texto = ''
    fecha = timezone.now()
    mes = fecha.strftime('%B')

    if collect_account.contract.contratista.usuario_asociado != None:
        municipio = collect_account.contract.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = collect_account.contract.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio,departamento)


    if collect_account.value_fees.amount.__float__()%1000000.00 == 0 :
        texto = '{0} de pesos MTC.'.format(num2words(collect_account.value_fees.amount.__float__(), lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(collect_account.value_fees.amount.__float__(), lang='es_CO'))


    concepto = ''

    meses_text = collect_account.month
    years_text = collect_account.year

    if collect_account.contract.proyecto == None:
        if collect_account.contract.proyecto == None:
            concepto = 'Honorarios profesionales de {0} del año {1}, contrato {2}.'.format(
                meses_text,
                years_text,
                collect_account.contract.nombre
            )
        else:
            concepto = 'Honorarios profesionales de {0} del año {1}, contrato {2} en el marco del proyecto {3}.'.format(
                meses_text,
                years_text,
                collect_account.contract.nombre,
                collect_account.contract.proyecto.nombre
            )
    else:
        if collect_account.contract.proyecto == None:
            concepto = 'Honorarios profesionales de {0} del año {1} en el cargo de {2}, contrato {3}.'.format(
                meses_text,
                years_text,
                collect_account.contract.cargo,
                collect_account.contract.nombre
            )
        else:
            concepto = 'Honorarios profesionales de {0} del año {1} en el cargo de {2}, contrato {3} en el marco del proyecto {4}.'.format(
                meses_text,
                years_text,
                collect_account.contract.cargo,
                collect_account.contract.nombre,
                collect_account.contract.proyecto.nombre
            )




    honorarios = [
        {
            'insert': '\n'
        },
        {
            'attributes': {'bold': True},
            'insert': '{0}: '.format(collect_account.month)
        },
        {
            'insert': '{0}'.format(collect_account.get_value_fees())
        },
        {
            'attributes': {'header': 3},
            'insert': '\n'
        }
    ]




    ret = {
        'CPS': [
                    {
                        'insert': '\n\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'CUENTA DE COBRO'
                    },
                    {
                        'attributes': {'align': 'center', 'header': 1},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'Debe a:'
                    },
                    {
                        'attributes': {'align': 'center', 'header': 2},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': collect_account.contract.contratista.get_full_name().upper()
                    },
                    {
                        'insert': ', identificado con '
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'C.C'
                    },
                    {
                        'insert': ' '
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': str(collect_account.contract.contratista.cedula).upper()
                    },
                    {
                        'insert': expedicion
                    },
                    {
                        'attributes': {'align': 'justify', 'header': 3},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'La suma de:'
                    },
                    {
                        'attributes': {'align': 'center', 'header': 2},
                        'insert': '\n'
                    },
                    {
                        'attributes': {'align': 'center'},
                        'insert': '\n'
                    },
                    {
                        'insert': '${0}'.format(collect_account.value_fees)
                    },
                    {
                        'attributes': {'align': 'center', 'header': 3},
                        'insert': '\n'
                    },
                    {
                        'attributes': {'align': 'center'},
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'Son: '
                    },
                    {
                        'insert': texto
                    },
                    {
                        'attributes': {'header': 3},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'Por concepto de: '
                    },
                    {
                        'insert': concepto
                    },
                    {
                        'attributes': {'header': 3},
                        'insert': '\n'
                    },
                ] + honorarios + [
                    {
                        'insert': '\nDada en __________________, a los ______ dias del mes de _________________ del año __________.'
                    },
                    {
                        'attributes': {'header': 3},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'Firma: _____________________'
                    },
                    {
                        'attributes': {'header': 3},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'bold': True},
                        'insert': 'Cédula: _____________________'
                    },
                    {
                        'attributes': {'header': 3},
                        'insert': '\n'
                    },
                    {
                        'insert': '\n\n'
                    },
                    {
                        'attributes': {'header': 3,'bold': False},
                        'insert': '\n'
                    },
                    {
                        'insert': '\nPor favor aplicar la retención sobre el articulo 383 del estatuto tributario en razón a que a la fecha no he contratado o vinculado dos (2) o más trabajadores asociados a la actividad que desarrollo'
                    },
               ]
    }

    return ret

def cuenta_transporte(collect_account):
    expedicion = ''
    texto = ''
    fecha = timezone.now()
    mes = fecha.strftime('%B')

    if collect_account.contract.contratista.usuario_asociado != None:
        municipio = collect_account.contract.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = collect_account.contract.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio, departamento)

    if collect_account.value_transport.amount.__float__() % 1000000.00 == 0:
        texto = '{0} de pesos MTC.'.format(num2words(collect_account.value_transport.amount.__float__(), lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(collect_account.value_transport.amount.__float__(), lang='es_CO'))

    concepto = ''

    meses_text = collect_account.month
    years_text = collect_account.year

    if collect_account.contract.proyecto == None:
        if collect_account.contract.proyecto == None:
            concepto = 'Reintegro de transporte de {0} del año {1}, contrato {2}.'.format(
                meses_text,
                years_text,
                collect_account.contract.nombre
            )
        else:
            concepto = 'Reintegro de transporte de {0} del año {1}, contrato {2} en el marco del proyecto {3}.'.format(
                meses_text,
                years_text,
                collect_account.contract.nombre,
                collect_account.contract.proyecto.nombre
            )
    else:
        if collect_account.contract.proyecto == None:
            concepto = 'Reintegro de transporte de {0} del año {1} en el cargo de {2}, contrato {3}.'.format(
                meses_text,
                years_text,
                collect_account.contract.cargo,
                collect_account.contract.nombre
            )
        else:
            concepto = 'Reintegro de transporte de {0} del año {1} en el cargo de {2}, contrato {3} en el marco del proyecto {4}.'.format(
                meses_text,
                years_text,
                collect_account.contract.cargo,
                collect_account.contract.nombre,
                collect_account.contract.proyecto.nombre
            )

    honorarios = [
        {
            'insert': '\n'
        },
    ]

    lista = [
        {
            'attributes': {'bold': True},
            'insert': '{0}: '.format(collect_account.month)
        },
        {
            'insert': '{0}'.format(collect_account.get_value_transport())
        },
        {
            'attributes': {'header': 3},
            'insert': '\n'
        }
    ]

    honorarios = honorarios + lista

    ret = {
        'CPS': [
                   {
                       'insert': '\n\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'CUENTA DE COBRO'
                   },
                   {
                       'attributes': {'align': 'center', 'header': 1},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'Debe a:'
                   },
                   {
                       'attributes': {'align': 'center', 'header': 2},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': collect_account.contract.contratista.get_full_name().upper()
                   },
                   {
                       'insert': ', identificado con '
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'C.C'
                   },
                   {
                       'insert': ' '
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': str(collect_account.contract.contratista.cedula).upper()
                   },
                   {
                       'insert': expedicion
                   },
                   {
                       'attributes': {'align': 'justify', 'header': 3},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'La suma de:'
                   },
                   {
                       'attributes': {'align': 'center', 'header': 2},
                       'insert': '\n'
                   },
                   {
                       'attributes': {'align': 'center'},
                       'insert': '\n'
                   },
                   {
                       'insert': '${0}'.format(collect_account.value_transport)
                   },
                   {
                       'attributes': {'align': 'center', 'header': 3},
                       'insert': '\n'
                   },
                   {
                       'attributes': {'align': 'center'},
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'Son: '
                   },
                   {
                       'insert': texto
                   },
                   {
                       'attributes': {'header': 3},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'Por concepto de: '
                   },
                   {
                       'insert': concepto
                   },
                   {
                       'attributes': {'header': 3},
                       'insert': '\n'
                   },
               ] + honorarios + [
                   {
                       'insert': '\nDada en __________________, a los ______ dias del mes de _________________ del año __________.'
                   },
                   {
                       'attributes': {'header': 3},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'Firma: _____________________'
                   },
                   {
                       'attributes': {'header': 3},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'bold': True},
                       'insert': 'Cédula: _____________________'
                   },
                   {
                       'attributes': {'header': 3},
                       'insert': '\n'
                   },
                   {
                       'insert': '\n\n'
                   },
                   {
                       'attributes': {'header': 3, 'bold': False},
                       'insert': '\n'
                   },
                   {
                       'insert': '\nPor favor aplicar la retención sobre el articulo 383 del estatuto tributario en razón a que a la fecha no he contratado o vinculado dos (2) o más trabajadores asociados a la actividad que desarrollo'
                   },
               ]
    }

    return ret


def numero_to_letras(numero):
    indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
    entero = int(numero)
    decimal = int(round((numero - entero) * 100))
    # print 'decimal : ',decimal
    contador = 0
    numero_letras = ""
    while entero > 0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a, 1).strip()
        else:
            en_letras = convierte_cifra(a, 0).strip()
        if a == 0:
            numero_letras = en_letras + " " + numero_letras
        elif a == 1:
            if contador in (1, 3):
                numero_letras = indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
        else:
            numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras

    return numero_letras


def convierte_cifra(numero, sw):
    lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS",
                     "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
    lista_decena = ["", (
    "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                    ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                    ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                    ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                    ("NOVENTA", "NOVENTA Y ")
                    ]
    lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
    centena = int(numero / 100)
    decena = int((numero - (centena * 100)) / 10)
    unidad = int(numero - (centena * 100 + decena * 10))
    # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

    texto_centena = ""
    texto_decena = ""
    texto_unidad = ""

    # Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad) != 0:
            texto_centena = texto_centena[1]
        else:
            texto_centena = texto_centena[0]

    # Valida las decenas
    texto_decena = lista_decena[decena]
    if decena == 1:
        texto_decena = texto_decena[unidad]
    elif decena > 1:
        if unidad != 0:
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
    # Validar las unidades
    # print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]

    return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)