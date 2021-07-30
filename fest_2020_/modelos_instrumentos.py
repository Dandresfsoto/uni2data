#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fest_2020_ import models, forms

modelos = {
    'documento_1':{
        'model':models.Documento,
        'form':forms.DocumentoForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/documento.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/documento_ver.html'
    },
    'acta_socializacion_comunidades':{
        'model':models.ActaSocializacionComunidades,
        'form':forms.ActaSocializacionComunidadesForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/actasocializacioncomunidades.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/actasocializacioncomunidades_ver.html'
    },
    'acta_vinculacion_hogar':{
        'model':models.ActaVinculacionHogar,
        'form':forms.ActaVinculacionHogarForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/acta_vinculacion_hogar.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/acta_vinculacion_hogar_ver.html'
    },
    'acta_socializacion_concertacion':{
        'model':models.ActaSocializacionConcertacion,
        'form':forms.ActaSocializacionConcertacionForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/acta_socializacion_concertacion.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/acta_socializacion_concertacion_ver.html'
    },
    'formulario_caracterizacion':{
        'model':models.FormularioCaracterizacion,
        'form':forms.FormularioCaracterizacionForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/formulario_caracterizacion.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/formulario_caracterizacion_ver.html'
    },
    'ficha_icoe':{
        'model':models.FichaIcoe,
        'form':forms.FichaIcoeForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/ficha_icoe.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/ficha_icoe_ver.html'
    },
    'ficha_vision_desarrollo':{
        'model':models.FichaVisionDesarrollo,
        'form':forms.FichaVisionDesarrolloForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/ficha_vision_desarrollo.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/ficha_vision_desarrollo_ver.html'
    },
    'diagnostico_comunitario':{
        'model':models.DiagnosticoComunitario,
        'form':forms.DiagnosticoComunitarioForm,
        'template':'fest_2020_1/misrutas/actividades/instrumentos/templates/diagnostico_comunitario.html',
        'template_ver':'fest_2020_1/misrutas/actividades/instrumentos/templates/diagnostico_comunitario_ver.html'
    },
    #Un documento pdf + 1 imagen para el soporte GForms
    'visita_3_vmc': {
        'model': models.DocumentoSoporteGmail,
        'form': forms.Visita_3_vmc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_vmc_ver.html'
    },

    #Un documento pdf + 1 imagen + 1 audio
    'documento_soporte_audio': {
        'model': models.DocumentoSoporteAudio,
        'form': forms.DocumentoSoporteAudioForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporteaudio.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporteaudio_ver.html'
    },

    'visita_5_sa': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_5_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_sa_ver.html'
    },

    'visita_6_fsc': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_6_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_fsc_ver.html'
    },
    'Soporte_audio3': {
        'model': models.SoporteAudio3,
        'form': forms.SoporteAudio3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/soporteaudio3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/soporteaudio3_ver.html'
    },
    'visita_6_pp(PP)': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_6_pp_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_pp_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_pp_pp_ver.html'
    },
    'visita_7_fsc': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_7_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_fsc_ver.html'
    },
    'visita_8_fsc': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_8_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_8_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_8_fsc_ver.html'
    },
    'visita_9_fsc': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_9_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_9_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_9_fsc_ver.html'
    },
    'visita_5_fsc': {
        'model': models.DocumentoSoporteAudio3,
        'form': forms.Visita_5_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_fsc_ver.html'
    },

    'visita_4_sa': {
        'model': models.DocumentoSoporteFotos2Audio3,
        'form': forms.Visita_4_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_sa_ver.html'
    },

    'taller_2_fsc': {
        'model': models.Taller_2_fsc,
        'form': forms.Taller_2_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_fsc_ver.html'
    },

    'taller_2_sa': {
        'model': models.Taller_2_sa,
        'form': forms.Taller_2_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_sa_ver.html'
    },

    'taller_2_pp': {
        'model': models.Taller_2_sa,
        'form': forms.Taller_2_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_pp_ver.html'
    },
    'taller_2_vmc': {
        'model': models.Taller_2_vmc,
        'form': forms.Taller_2_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_2_vmc_ver.html'
    },

    #Un documento pdf + 1 imagen para el soporte GForms + 2 fotos
    'visita_3_sa': {
        'model': models.DocumentoSoporteGformsFotos2,
        'form': forms.Visita_3_sa_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_sa_ver.html'
    },
    #Un documento pdf + 1 imagen para el soporte + 2 fotos + 1 audio
    'documento_soporte_fotos2_audio': {
        'model': models.DocumentoSoporteFotos2Audio,
        'form': forms.DocumentoSoporteFotos2AudioForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotos2audio.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotos2audio_ver.html'
    },
    #Un documento pdf + 1 imagen para el soporte + 2 fotos + 1 audio
    'visita_4_vmc': {
        'model': models.DocumentoSoporteFotos2Audio3,
        'form': forms.Visita_4_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_vmc_ver.html'
    },
    'dispersionyprooveduria': {
        'model': models.DocumentoSoporte2Fotos2Audio3,
        'form': forms.DispersionyprooveduriaForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/dispersionyprooveduria.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/dispersionyprooveduria_ver.html'
    },
    'vista_7_pp': {
        'model': models.DocumentoSoporte2Fotos2Audio3,
        'form': forms.Visita_7_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_pp_ver.html'
    },
    'vista_7_pp(PP)': {
        'model': models.DocumentoSoporte2Fotos2Audio3,
        'form': forms.Visita_7_pp_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_pp_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_pp_pp_ver.html'
    },
    'documento_soporte2_fotos_audio3': {
        'model': models.DocumentoSoporteFotos2Audio3,
        'form': forms.DocumentoSoporte2FotosAudio3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotos2audio3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte2fotosaudio3_ver.html'
    },

    'visita_7_sa': {
        'model': models.DocumentoSoporteFotos2Audio3,
        'form': forms.Visita_7_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_7_sa_ver.html'
    },

    'documento_soporte2_fotos2_audio3': {
        'model': models.DocumentoSoporte2Fotos2Audio3,
        'form': forms.DocumentoSoporte2Fotos2Audio3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte2fotos2audio3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte2fotos2audio3_ver.html'
    },
    'huerta_comunitaria': {
        'model': models.DocumentoSoporte2Fotos2Audio3,
        'form': forms.HuertacomunitariaForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/huertacomunitaria.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/huertacomunitaria_ver.html'
    },
    'documento_soporte_fotos_audio3': {
        'model': models.DocumentoSoporteFotosAudio3,
        'form': forms.DocumentoSoporteFotosAudio3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotosaudio3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotosaudio3_ver.html'
    },
    'visita_9_pp': {
        'model': models.DocumentoSoporteFotosAudio3,
        'form': forms.Visita_9_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotosaudio3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoportefotosaudio3_ver.html'
    },
    #Un documento pdf + 2 fotos
    'visita_3_fsc': {
        'model': models.DocumentoFotos2,
        'form': forms.Visita_3_fsc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_fsc_ver.html'
    },

    #Un documento pdf + 2 fotos + audio
    'documento_fotos2_audio': {
        'model': models.DocumentoFotos2Audio,
        'form': forms.DocumentoFotos2AudioForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosfotos2audio.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosfotos2audio_ver.html'
    },
    'visita_4_fsc': {
        'model': models.Documento2Fotos2,
        'form': forms.Visita_4_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_fsc_ver.html'
    },
    'visita_6_pp': {
        'model': models.Documento2Fotos2,
        'form': forms.Visita_6_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_pp_ver.html'
    },
    'visita_5_vmc': {
        'model': models.Documento2Fotos2,
        'form': forms.Visita_5_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_vmc_ver.html'
    },
    'documento2_foto': {
        'model': models.Documento2Foto,
        'form': forms.Documento2FotoForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soporte.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2foto_ver.html'
    },
    #Un documento pdf + 2 soportes + 1 foto
    'documento_soporte2_foto': {
        'model': models.DocumentoSoporte2Fotos,
        'form': forms.DocumentoSoporte2FotoForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte2foto.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte2foto_ver.html'
    },
    # Dos documento pdf + 1 Soporte
    'visita_4_pp': {
        'model': models.Documento2Soporte,
        'form': forms.Visita_4_PPForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_4_pp_ver.html'
    },
    'visita_5_pp': {
        'model': models.Documento2SoporteFotos2,
        'form': forms.Visita_5_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_5_pp_ver.html'
    },
    # documento pdf + 3 soporte + 2 fotos
    'documento_soporte3_fotos2': {
        'model': models.DocumentoSoporte3Fotos2,
        'form': forms.DocumentoSoporte3Fotos2Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte3fotos2.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentosoporte3fotos2_ver.html'
    },

    'taller_3_pp': {
        'model': models.Documento3Soporte,
        'form': forms.Taller_3_pp_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_pp_ver.html'
    },

    'visita_6_sa': {
        'model': models.Documento3Soporte,
        'form': forms.Visita_6_sa_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_6_sa_ver.html'
    },

    'visita_3_pp': {
        'model': models.DocumentoSoporte2,
        'form': forms.Visita_3_pp_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_3_pp_ver.html'
    },
    # 2 documento pdf + 2 soporte + 3 fotos
    'documento2_soporte2_fotos3': {
        'model': models.Documento2Soporte2Fotos3,
        'form': forms.Documento2Soporte2Fotos3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soporte2fotos3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soporte2fotos3_ver.html'
    },
    # 3 documento pdf + 2 soporte + 3 fotos
    'documento2_soporte_fotos3': {
        'model': models.Documento2SoporteFotos3,
        'form': forms.Documento2SoporteFotos3Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soportefotos3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soportefotos3_ver.html'
    },
    # 3 documento pdf + 2 soporte + 3 fotos
    'jic_2_fsc': {
        'model': models.Documento3SoporteFotos3,
        'form': forms.Jic_2_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_fsc_ver.html'
    },
    'otros_8_pp': {
        'model': models.Documento3SoporteFotos3,
        'form': forms.Otros_8_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/otros_8_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/otros_8_pp_ver.html'
    },
    'taller_4_sa': {
        'model': models.Documento3Soporte2Fotos3Foto,
        'form': forms.Taller_4_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_sa_ver.html'
    },
    'taller_5_sa': {
        'model': models.Documento3SoporteFotos3,
        'form': forms.Taller_5_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_sa_ver.html'
    },
    'taller_3_fsc': {
        'model': models.Documento4SoporteFotos3,
        'form': forms.Taller_3_fsc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_fsc_ver.html'
    },
    'taller_6_fsc': {
        'model': models.Documento4SoporteFotos3,
        'form': forms.Taller_6_fsc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_fsc_ver.html'
    },
    'taller_5_fsc': {
        'model': models.Documento4SoporteFotos3,
        'form': forms.Taller_5_fsc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_fsc_ver.html'
    },

    'entrega_huerta_casera': {
        'model': models.Documento2SoporteFotos4,
        'form': forms.EntregahuertacaseraForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/entregahuertacasera.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/entregahuertacasera_ver.html'
    },
    'Jic_1_sa': {
        'model': models.Documento4SoporteFotos3Fotos4,
        'form': forms.jic_1_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_sa_ver.html'
    },
    'taller_8_pp': {
        'model': models.Documento4SoporteFotos3Fotos4,
        'form': forms.taller_8_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_8_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_8_pp_ver.html'
    },
    'taller_3_vmc': {
        'model': models.Documento3Fotos3,
        'form': forms.Taller_3_vmc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_vmc_ver.html'
    },

    'huerta_comunitaria_sa': {
        'model': models.Documento3Fotos3,
        'form': forms.huertacomunitariasaForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/huertacomunitaria_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/huertacomunitaria_sa_ver.html'
    },

    'taller_3_sa': {
        'model': models.Documento4Soportes3,
        'form': forms.Taller_3_sa_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_3_sa_ver.html'
    },
    'taller_4_fsc': {
        'model': models.Documento4Soportes3,
        'form': forms.Taller_4_fsc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_fsc_ver.html'
    },
    'taller_6_pp(PP)': {
        'model': models.Documento4Soportes4,
        'form': forms.Taller_6_pp_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_pp_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_pp_pp_ver.html'
    },
    # 6 pdf+ 3 soportes
    'jic_2_vmc': {
        'model': models.Documento6Fotos3,
        'form': forms.Jic_2_vmc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_vmc_ver.html'
    },
    'taller_4_vmc': {
        'model': models.Documento6Fotos3,
        'form': forms.Taller_4_vmc_Form,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_vmc_ver.html'
    },
    'Jic_1_fsc': {
        'model': models.Documento4SoporteFotos4Fotos4,
        'form': forms.jic_1_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_fsc_ver.html'
    },
    'jic_5_fsc': {
        'model': models.Documento4SoporteFotos4Fotos4,
        'form': forms.jic_5_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_5_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_5_fsc_ver.html'
    },
    'Jic_1_pp': {
        'model': models.Documento4SoporteFotos4Fotos4,
        'form': forms.jic_1_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_pp_ver.html'
    },
    'Jic_1_vmc': {
        'model': models.Documento4SoporteFotos4Fotos4,
        'form': forms.jic_1_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_1_vmc_ver.html'
    },

    # 4 pdf 4 fotos + 4 foto extra
    'jic_2_pp': {
        'model': models.Documento4Fotos4Fotos4,
        'form': forms.jic_2_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_2_pp_ver.html'
    },
    # 2 pdf
    'documento2': {
        'model': models.Documento2,
        'form': forms.DispersionyprooveduriappForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/dispersionyprooveduriapp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/dispersionyprooveduriapp_ver.html'
    },
    'jic_3_sa': {
        'model': models.DocumentoFotos4,
        'form': forms.Jic_3_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_sa_ver.html'
    },
    'jic_4_pp': {
        'model': models.DocumentoFotos4,
        'form': forms.Jic_4_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_pp_ver.html'
    },
    'taller_4_pp': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_4_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_4_pp_ver.html'
    },
    'taller_7_pp(PP)': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_7_pp_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_7_pp_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_7_pp_pp_ver.html'
    },
    'taller_6_pp': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_6_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_pp_ver.html'
    },
    'taller_5_pp': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_5_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_pp_ver.html'
    },
    'taller_5_vmc': {
        'model': models.Documento3SoporteFotos2,
        'form': forms.Taller_5_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_5_vmc_ver.html'
    },
    'jic_5_pp': {
        'model': models.Documento3SoporteFotos2,
        'form': forms.Jic_5_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_5_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_5_pp_ver.html'
    },
    'visita_8_pp': {
        'model': models.Documento3SoporteFotos2,
        'form': forms.visita_8_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_8_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/visita_8_pp_ver.html'
    },
    'taller_7_fsc': {
        'model': models.Documento3SoporteFotos2,
        'form': forms.Taller_7_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_7_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_7_fsc_ver.html'
    },
    'taller_6_sa': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_6_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_6_sa_ver.html'
    },
    'taller_8_fsc': {
        'model': models.Documento3SoporteFotos4,
        'form': forms.Taller_8_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_8_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/taller_8_fsc_ver.html'
    },
    'jic_3_fsc': {
        'model': models.Documento4Fotos5,
        'form': forms.Jic_3_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_fsc_ver.html'
    },
    'jic_3_pp': {
        'model': models.Documento4Fotos5,
        'form': forms.Jic_3_ppForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_pp.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_3_pp_ver.html'
    },
    'jic_4_fsc': {
        'model': models.Documento4Fotos5,
        'form': forms.Jic_4_fscForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_fsc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_fsc_ver.html'
    },
    'jic_4_sa': {
        'model': models.Documento4Fotos5,
        'form': forms.Jic_4_saForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_sa.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_sa_ver.html'
    },
    'jic_4_vmc': {
        'model': models.Documento4Fotos5,
        'form': forms.Jic_4_vmcForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_vmc.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/jic_4_vmc_ver.html'
    },
    # 2 documento pdf + 2 soporte + 3 fotos
    'documento_general': {
        'model': models.DocumentoGeneral,
        'form': forms.DocumentoGeneralForm,
        'template': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soporte2fotos3.html',
        'template_ver': 'fest_2020_1/misrutas/actividades/instrumentos/templates/documentos2soporte2fotos3_ver.html'
    },
}


def get_modelo(key):
    return modelos[key]