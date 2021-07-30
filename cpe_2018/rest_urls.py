from django.urls import path, include
from cpe_2018 import rest_views

urlpatterns = [


    path('bd/', rest_views.RegionesListApi.as_view()),
    path('bd/actualizar/', rest_views.ActualizacionRadicadosListApi.as_view()),
    path('bd/actualizar_docentes/', rest_views.ActualizacionDocentesListApi.as_view()),

    path('bd/<uuid:pk>/', rest_views.DepartamentosListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/', rest_views.MunicipiosListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/radicados/', rest_views.RadicadosListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/docentes/', rest_views.DocentesListApi.as_view()),


    path('componentes/', rest_views.ComponentesListApi.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/', rest_views.EstrategiasListApi.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/<uuid:pk_estrategia>/momentos/', rest_views.MomentosListApi.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/<uuid:pk_estrategia>/momentos/<uuid:pk_momento>/entregables/', rest_views.EntregablesListApi.as_view()),

    path('formacion/', include('formacion.rest_urls')),
    path('entes_territoriales/', include('entes_territoriales.rest_urls')),
    path('solicitudes_desplazamiento/', include('desplazamiento.rest_urls')),
    path('formatos/', include('formatos.rest_urls')),

    path('rutas/<uuid:pk>/', rest_views.RutasRegionListApi.as_view()),
    path('liquidaciones/<uuid:pk>/', rest_views.LiquidacionRutasRegionListApi.as_view()),



    path('informes/<uuid:pk>/matricula/', rest_views.InformesMatriculaAPI.as_view()),
    path('informes/<uuid:pk>/sedes/', rest_views.InformesSedesAPI.as_view()),
    path('informes/<uuid:pk>/retoma/', rest_views.InformesRetomaAPI.as_view()),
    path('informes/<uuid:pk>/formacion/', rest_views.InformesFormacionAPI.as_view()),


    path('soportes/<uuid:pk>/sedes/', rest_views.RadicadosSoportesListApi.as_view()),
    path('soportes/<uuid:pk>/sedes/ver/<uuid:pk_radicado>/', rest_views.RadicadosVerSoportesListApi.as_view()),

    path('soportes/<uuid:pk>/docentes/', rest_views.DocentesSoportesListApi.as_view()),
    path('soportes/<uuid:pk>/docentes/ver/<uuid:pk_docente>/', rest_views.DocentesVerSoportesListApi.as_view()),

    path('soportes/<uuid:pk>/retomas/', rest_views.RetomasSoportesListApi.as_view()),


    #------------------------------------- CUENTAS COBRO -------------------------------------


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/', rest_views.RutasCuentasCobroListApi.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', rest_views.RutasCuentasCobroDetalleListApi.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/', rest_views.RutasCuentasCobroDetalleComponenteListApi.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/', rest_views.RutasCuentasCobroDetalleRetomaListApi.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', rest_views.RutasCuentasCobroDetalleRadicadoListApi.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesSedeCuentasCobroListApi.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesSedeRutaCuentaCobroListApi.as_view()),


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/', rest_views.GruposRutaCuentaCobroListApi.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/', rest_views.ActividadesGrupoCuentaCobroRutaListApi.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', rest_views.EvidenciasFormacionRutaCuentaCobroListApi.as_view()),

    #----------------------------------------------------------------------------------


    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/', rest_views.ActividadesRutaListApi.as_view()),




    path('rutas/mapa/<uuid:pk>/', rest_views.RutasMapaApiJson.as_view()),
    path('rutas/trazabilidad/<uuid:pk>/', rest_views.RutasTrazabilidadApiJson.as_view()),

    #path(
    #    'rutas/trazabilidad/<uuid:pk>/actividades/<uuid:pk_ruta>/actividad/<uuid:pk_actividad>/actividad_ruta/<uuid:pk_actividad_ruta>/',
    #    rest_views.ActividadesRutasTrazabilidadApiJson.as_view()),

    path('rutas/autocomplete/contratos/', rest_views.ContratosAutocomplete.as_view()),
    path('rutas/autocomplete/contratistas/', rest_views.ContratistaAutocomplete.as_view()),
    path('rutas/autocomplete/radicados/<uuid:pk>/', rest_views.RadicadosAutocomplete.as_view()),




    #------------------------------------- ACCESO -------------------------------------

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/', rest_views.ActividadesComponenteRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/', rest_views.ActividadesRetomaRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesSedeRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', rest_views.ActividadesComponenteRadicadoRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesSedeListApi.as_view()),

    path('rutas/autocomplete/municipios/', rest_views.MunicipiosAutocomplete.as_view()),
    path('rutas/autocomplete/municipios/<uuid:pk_region>/', rest_views.MunicipiosAutocompleteRegion.as_view()),

    #----------------------------------------------------------------------------------

    #----------------------------------- FORMACIÓN ------------------------------------

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/', rest_views.GruposRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/', rest_views.DocentesGrupoRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/', rest_views.ActividadesGrupoRutaListApi.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', rest_views.EvidenciasFormacionRutaListApi.as_view()),


    path('rutas/autocomplete/docentes/<uuid:pk_grupo>/<uuid:pk_region>/', rest_views.DocentesAutocomplete.as_view()),

    #----------------------------------------------------------------------------------

    #----------------------------------- MIS RUTAS ------------------------------------

    path('misrutas/', rest_views.MisRutasListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/', rest_views.MisRutasCuentasCobroListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/', rest_views.ActividadesMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/', rest_views.ActividadesComponenteMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/', rest_views.ActividadesRetomaMisRutasListApi2.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesSedeMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', rest_views.ActividadesComponenteRadicadoMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', rest_views.ActividadesRadicadoSedeMisRutasListApi.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/formacion/', rest_views.GruposMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/', rest_views.DocentesGrupoMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/', rest_views.ActividadesGrupoMisRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', rest_views.EvidenciasFormacionMisRutasListApi.as_view()),



    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', rest_views.MisRutasCuentasCobroDetalleListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/', rest_views.MisRutasCuentasCobroDetalleComponenteListApi.as_view()),

    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/', rest_views.MisRutasCuentasCobroDetalleRetomaListApi.as_view()),

    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', rest_views.MisRutasCuentasCobroDetalleRadicadoListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', rest_views.MisActividadesSedeCuentasCobroListApi.as_view()),

    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', rest_views.MisActividadesSedeRutaCuentaCobroListApi.as_view()),


    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/', rest_views.MisGruposRutaCuentaCobroListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/', rest_views.MisActividadesGrupoCuentaCobroRutaListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', rest_views.MisEvidenciasFormacionRutaCuentaCobroListApi.as_view()),



    #----------------------------------------------------------------------------------


    path('cortes/<uuid:pk>/', rest_views.CortesRegionListApi.as_view()),
    path('cortes/<uuid:pk>/ver/<uuid:pk_corte>/', rest_views.CortesRegionCuentasCobroListApi.as_view()),

    #----------------------------------- MIS RUTAS ------------------------------------

    path('red/<uuid:pk>/', rest_views.RedRegionListApi.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/', rest_views.RedRegionVerApi.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/actividades/<uuid:pk_entregable>/', rest_views.RedRegionVerEntregablesApi.as_view()),

    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/', rest_views.RedsRegionVerActividadesEstrategiaApi.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/calificar/<uuid:pk_entregable>/', rest_views.RedRegionVerEntregablesFormacionApi.as_view()),

    #----------------------------------------------------------------------------------
]