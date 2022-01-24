import json

from num2words import num2words
from PyPDF2 import PdfFileMerger
from recursos_humanos.models import *
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
            if contrato.cargo.obligaciones == None:
                contratos.append({
                    'attributes': {'align': 'justify'},
                    'insert': '\n'
                })
            else:
                contratos.append({
                    'attributes': {'bold': True},
                    'insert': 'Obligaciones del contratista :'
                })
                contratos.append({
                    'attributes': {'align': 'justify'},
                    'insert': '\n'
                })
                contratos.append({
                    'attributes': {'align': 'justify','list':'ordered'},
                    'insert': contrato.get_obligaciones()
                })
                contratos.append({
                    'attributes': {'align': 'justify','list':'ordered'},
                    'insert': '\n'
                })
                contratos.append({
                    'attributes': {'align': 'justify'},
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
                    'insert': 'ASOCIACIÓN COLOMBIANA DE INNOVACIÓN'
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
                    'insert': 'NIT. 901.294.654-6'
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
                    'insert': 'Que en el sistema de información UNI2DATA se encuentra registrada la siguiente información de '
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

def delta_empty():

    ret = {
            'ops':[

                {
                    'insert': '\n'
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

def month_converter(month):
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    return months[month]

def es_bisiesto(anio: int) -> bool:
    return anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)

def obtener_dias_del_mes(mes: int, anio: int) -> int:
    # Abril, junio, septiembre y noviembre tienen 30
    if mes in [4, 6, 9, 11]:
        return 30
    # Febrero depende de si es o no bisiesto
    if mes == 2:
        if es_bisiesto(anio):
            return 29
        else:
            return 28
    else:
        # En caso contrario, tiene 31 días
        return 31

def delta_cuenta_cobro_parcial(liquidacion,valor,mes,year):

    expedicion = ''
    texto = ''
    fecha = timezone.now()

    if liquidacion.contrato.contratista.usuario_asociado != None:
        municipio = liquidacion.contrato.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = liquidacion.contrato.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio,departamento)


    if valor%1000000.00 == 0 :
        texto = '{0} de pesos MTC.'.format(num2words(valor, lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(valor, lang='es_CO'))


    concepto = ''


    if liquidacion.contrato.cargo == None:

        if liquidacion.contrato.proyecto == None:
            concepto = 'Honorarios profesionales mes de {0} del año {1}, contrato {2}.'.format(
                            mes,
                            year,
                            liquidacion.contrato.nombre
                        )
        else:
            concepto = 'Honorarios profesionales mes de {0} del año {1}, contrato {2} en el marco del proyecto {3}.'.format(
                mes,
                year,
                liquidacion.contrato.nombre,
                liquidacion.contrato.proyecto.nombre
            )
    else:
        if liquidacion.contrato.proyecto == None:
            concepto = 'Honorarios profesionales mes de {0} del año {1} en el cargo de {2}, contrato {3}.'.format(
                mes,
                year,
                liquidacion.contrato.cargo,
                liquidacion.contrato.nombre
            )
        else:
            concepto = 'Honorarios profesionales mes de {0} del año {1} en el cargo de {2}, contrato {3} en el marco del proyecto {4}.'.format(
                mes,
                year,
                liquidacion.contrato.cargo,
                liquidacion.contrato.nombre,
                liquidacion.contrato.proyecto.nombre
            )


    ret = {
        'ops': [
                    {
                        'insert': 'ID: {0}'.format(liquidacion.id)
                    },
                    {
                        'attributes': {'bold': True, 'align':'right','size':'8px'},
                        'insert': '\n'
                    },
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
                        'insert': liquidacion.contrato.contratista.get_full_name().upper()
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
                        'insert': str(liquidacion.contrato.contratista.cedula).upper()
                    },
                    {
                        'insert': expedicion
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
                        'insert': '${:20,.2f}'.format(valor).replace(' ','')
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
                        'attributes': {'align': 'justify','header': 3},
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