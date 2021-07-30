#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fest_2019 import models, forms

modelos = {
    'documento_1':{
        'model':models.Documento,
        'form':forms.DocumentoForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/documento.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/documento_ver.html'
    },
    'acta_socializacion_comunidades':{
        'model':models.ActaSocializacionComunidades,
        'form':forms.ActaSocializacionComunidadesForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/acta_socializacion_comunidades.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/acta_socializacion_comunidades_ver.html'
    },
    'acta_vinculacion_hogar':{
        'model':models.ActaVinculacionHogar,
        'form':forms.ActaVinculacionHogarForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/acta_vinculacion_hogar.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/acta_vinculacion_hogar_ver.html'
    },
    'acta_socializacion_concertacion':{
        'model':models.ActaSocializacionConcertacion,
        'form':forms.ActaSocializacionConcertacionForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/acta_socializacion_concertacion.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/acta_socializacion_concertacion_ver.html'
    },
    'formulario_caracterizacion':{
        'model':models.FormularioCaracterizacion,
        'form':forms.FormularioCaracterizacionForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/formulario_caracterizacion.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/formulario_caracterizacion_ver.html'
    },
    'ficha_icoe':{
        'model':models.FichaIcoe,
        'form':forms.FichaIcoeForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/ficha_icoe.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/ficha_icoe_ver.html'
    },
    'ficha_vision_desarrollo':{
        'model':models.FichaVisionDesarrollo,
        'form':forms.FichaVisionDesarrolloForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/ficha_vision_desarrollo.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/ficha_vision_desarrollo_ver.html'
    },
    'diagnostico_comunitario':{
        'model':models.DiagnosticoComunitario,
        'form':forms.DiagnosticoComunitarioForm,
        'template':'fest_2019/misrutas/actividades/instrumentos/templates/diagnostico_comunitario.html',
        'template_ver':'fest_2019/misrutas/actividades/instrumentos/templates/diagnostico_comunitario_ver.html'
    },
}


def get_modelo(key):
    return modelos[key]