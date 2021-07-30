import json
from num2words import num2words
from django.utils import timezone
from cpe_2018 import models
from fest_2020_ import models

def delta_cuenta_cobro(cuenta_cobro):

    expedicion = ''
    texto = ''
    fecha = timezone.now()
    mes = fecha.strftime('%B')

    if cuenta_cobro.ruta.contrato.contratista.usuario_asociado != None:
        municipio = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio,departamento)


    if cuenta_cobro.valor.amount.__float__()%1000000.00 == 0 :
        texto = '{0} de pesos MTC.'.format(num2words(cuenta_cobro.valor.amount.__float__(), lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(cuenta_cobro.valor.amount.__float__(), lang='es_CO'))


    concepto = ''

    if cuenta_cobro.data_json == '' or cuenta_cobro.data_json == None:
        meses_text = '<<meses>>'
        year_text = '<<year>>'
    else:
        mes = json.loads(cuenta_cobro.data_json)['mes']
        year = json.loads(cuenta_cobro.data_json)['year']
        years_text = year

        meses_text = mes
        pron = 'mes'

        if len(mes) == 1:
            pron = 'mes'
            meses_text = mes[0]
        elif len(mes) > 1:
            pron = 'meses'
            meses_text = ''

            for m in mes[:-1]:
                meses_text += m + ', '

            meses_text = meses_text[:-2] + ' y ' + mes[-1]



    if cuenta_cobro.ruta.contrato.cargo == None:

        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Honorarios profesionales {0} de {1} del año {2}, contrato {3}.'.format(
                            pron,
                            meses_text,
                            years_text,
                            cuenta_cobro.ruta.contrato.nombre
                        )
        else:
            concepto = 'Honorarios profesionales {0} de {1} del año {2}, contrato {3} en el marco del proyecto {4}.'.format(
                pron,
                meses_text,
                years_text,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )
    else:
        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Honorarios profesionales {0} de {1} del año {2} en el cargo de {3}, contrato {4}.'.format(
                pron,
                meses_text,
                years_text,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre
            )
        else:
            concepto = 'Honorarios profesionales {0} de {1} del año {2} en el cargo de {3}, contrato {4} en el marco del proyecto {5}.'.format(
                pron,
                meses_text,
                years_text,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )


    valores_json = json.loads(cuenta_cobro.valores_json)

    honorarios = [
        {
            'insert': '\n'
        },
    ]

    for valor in valores_json:

        lista = [
            {
                'attributes': {'bold': True},
                'insert': '{0}: '.format(valor.get('mes'))
            },
            {
                'insert': '{0}'.format(valor.get('valor'))
            },
            {
                'attributes': {'header': 3},
                'insert': '\n'
            }
        ]

        honorarios = honorarios + lista



    ret = {
        'ops': [
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
                        'insert': cuenta_cobro.ruta.contrato.contratista.get_full_name().upper()
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
                        'insert': str(cuenta_cobro.ruta.contrato.contratista.cedula).upper()
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
                        'insert': '${:20,.2f}'.format(cuenta_cobro.valor.amount).replace(' ','')
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
                ] + honorarios +[
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

def delta_cuenta_cobro_parcial(cuenta_cobro,valor,mes,year):

    expedicion = ''
    texto = ''
    fecha = timezone.now()

    if cuenta_cobro.ruta.contrato.contratista.usuario_asociado != None:
        municipio = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio,departamento)


    if valor%1000000.00 == 0 :
        texto = '{0} de pesos MTC.'.format(num2words(valor, lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(valor, lang='es_CO'))


    concepto = ''


    if cuenta_cobro.ruta.contrato.cargo == None:

        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Honorarios profesionales mes de {0} del año {1}, contrato {2}.'.format(
                            mes,
                            year,
                            cuenta_cobro.ruta.contrato.nombre
                        )
        else:
            concepto = 'Honorarios profesionales mes de {0} del año {1}, contrato {2} en el marco del proyecto {3}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )
    else:
        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Honorarios profesionales mes de {0} del año {1} en el cargo de {2}, contrato {3}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre
            )
        else:
            concepto = 'Honorarios profesionales mes de {0} del año {1} en el cargo de {2}, contrato {3} en el marco del proyecto {4}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )


    ret = {
        'ops': [
                    {
                        'insert': 'ID: {0}'.format(cuenta_cobro.id)
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
                        'insert': cuenta_cobro.ruta.contrato.contratista.get_full_name().upper()
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
                        'insert': str(cuenta_cobro.ruta.contrato.contratista.cedula).upper()
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

def delta_cuenta_transporte(cuenta_cobro,valor,mes,year):

    expedicion = ''
    texto = ''
    fecha = timezone.now()

    if cuenta_cobro.ruta.contrato.contratista.usuario_asociado != None:
        municipio = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.nombre
        departamento = cuenta_cobro.ruta.contrato.contratista.usuario_asociado.lugar_expedicion.departamento.nombre
        expedicion = ' expedida en {0}, {1}.'.format(municipio,departamento)


    if valor%1000000.00 == 0 :
        texto = '{0} de pesos MTC.'.format(num2words(valor, lang='es_CO'))
    else:
        texto = '{0} pesos MTC.'.format(num2words(valor, lang='es_CO'))


    concepto = ''


    if cuenta_cobro.ruta.contrato.cargo == None:

        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Reintegro de gastos por actividades asignadas del mes de {0} del año {1}, contrato {2}.'.format(
                            mes,
                            year,
                            cuenta_cobro.ruta.contrato.nombre
                        )
        else:
            concepto = 'Reintegro de gastos por actividades asignadas del mes de {0} del año {1}, contrato {2} en el marco del proyecto {3}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )
    else:
        if cuenta_cobro.ruta.contrato.proyecto == None:
            concepto = 'Reintegro de gastos por actividades asignadas del  mes de {0} del año {1} en el cargo de {2}, contrato {3}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre
            )
        else:
            concepto = 'Reintegro de gastos por actividades asignadas del mes de {0} del año {1} en el cargo de {2}, contrato {3} en el marco del proyecto {4}.'.format(
                mes,
                year,
                cuenta_cobro.ruta.contrato.cargo,
                cuenta_cobro.ruta.contrato.nombre,
                cuenta_cobro.ruta.contrato.proyecto.nombre
            )


    ret = {
        'ops': [
                    {
                        'insert': 'ID: {0}'.format(cuenta_cobro.id)
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
                        'insert': cuenta_cobro.ruta.contrato.contratista.get_full_name().upper()
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
                        'insert': str(cuenta_cobro.ruta.contrato.contratista.cedula).upper()
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
