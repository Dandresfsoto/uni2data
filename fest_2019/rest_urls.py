from django.urls import path, include
from fest_2019 import rest_views

urlpatterns = [
    path('proyectos_api/', rest_views.ProyectosApiView.as_view()),
    path('proyectos_api/<int:cedula>/', rest_views.ProyectosApiListView.as_view()),
    path('proyectos_api/<int:cedula>/<int:pk>/', rest_views.ProyectosApiRetrieveView.as_view()),


    path('georeferenciacion_api/', rest_views.GeoreferenciacionApiView.as_view()),
    path('georeferenciacion_api/<int:cedula>/', rest_views.GeoreferenciacionApiListView.as_view()),
    path('georeferenciacion_api/<int:cedula>/<int:pk>/', rest_views.GeoreferenciacionApiRetrieveView.as_view()),


    path('migeoreferenciacion/', rest_views.MiGeoreferenciacionListApi.as_view()),
    path('georeferenciacion/', rest_views.GeoreferenciacionListApi.as_view()),


    path('misproyectos/', rest_views.MisProyectosListApi.as_view()),
    path('proyectos_local/', rest_views.ProyectosLocalListApi.as_view()),
    path('proyectos_monitoreo/', rest_views.ProyectosMonitoreoListApi.as_view()),
    path('proyectos_especialistas/', rest_views.ProyectosEspecialistasListApi.as_view()),


    path('bd/', rest_views.HogaresListApi.as_view()),

    path('entregables/', rest_views.EntregablesListApi.as_view()),
    path('entregables/<uuid:pk_componente>/momentos/', rest_views.MomentosListApi.as_view()),
    path('entregables/<uuid:pk_componente>/momentos/<uuid:pk_momento>/instrumentos/', rest_views.InstrumentosListApi.as_view()),


    #------------------------------------- RUTAS -------------------------------------
    #Gestión de rutas
    path('rutas/', rest_views.RutasListApi.as_view()),  #permisos revisados


    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/', rest_views.InstrumentosHogaresRutasListApi.as_view()),     #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/trazabilidad/<uuid:pk_instrumento_object>/', rest_views.InstrumentosHogaresRutasTrazabilidadListApi.as_view()),   #Permisos revisados



    #------------------------------------- CUENTAS DE COBRO -------------------------------------

    path('rutas/cuentas_cobro/<uuid:pk_ruta>/', rest_views.RutasCuentasCobroListApi.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', rest_views.CorteHogaresActividadesListApi.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/', rest_views.CorteActividadesHogaresRutasListApi.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/', rest_views.CorteInstrumentosHogaresRutasListApi.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/trazabilidad/<uuid:pk_instrumento_object>/', rest_views.CorteInstrumentosHogaresRutasTrazabilidadListApi.as_view()),


    #Gestión de hogares
    path('rutas/hogares/<uuid:pk_ruta>/', rest_views.HogaresRutasListApi.as_view()), #permisos revisados
    path('rutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/', rest_views.MiembrosHogaresRutasListApi.as_view()),

    #Gestión de actividades
    path('rutas/actividades/<uuid:pk_ruta>/', rest_views.HogaresActividadesListApi.as_view()),#permisos revisados

    path('rutas/actividades/<uuid:pk_ruta>/objetos/<uuid:pk_momento>/', rest_views.HogaresActividadesObjetosListApi.as_view()),



    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/', rest_views.ActividadesHogaresRutasListApi.as_view()),   #permisos revisados

    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/trazabilidad/<uuid:pk_instrumento_object>/', rest_views.InstrumentosHogaresRutasTrazabilidadListApi.as_view()),   #Permisos revisados



    path('rutas/autocomplete/contratos/', rest_views.ContratosAutocomplete.as_view()),

    #----------------------------------- MIS RUTAS ------------------------------------

    path('misrutas/', rest_views.MisRutasListApi.as_view()),
    path('misrutas/hogares/<uuid:pk_ruta>/', rest_views.HogaresMisRutasListApi.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/', rest_views.MisInstrumentosHogaresRutasListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/observaciones/<uuid:pk_instrumento_object>/', rest_views.MisInstrumentosHogaresRutasObservacionesListApi.as_view()),


    path('misrutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/', rest_views.MiembrosHogaresMisRutasListApi.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/', rest_views.HogaresMisActividadesListApi.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/', rest_views.MisActividadesHogaresRutasListApi.as_view()),





    #----------------------------------- CUENTAS DE COBRO ------------------------------------

    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/', rest_views.MisRutasCuentasCobroListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', rest_views.MisCorteHogaresActividadesListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/', rest_views.MisCorteActividadesHogaresRutasListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/', rest_views.MisCorteInstrumentosHogaresRutasListApi.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/trazabilidad/<uuid:pk_instrumento_object>/', rest_views.MisCorteInstrumentosHogaresRutasTrazabilidadListApi.as_view()),




    path('misrutas/cargar-municipios/', rest_views.cargar_municipios),
    path('misrutas/cargar-corregimientos/', rest_views.cargar_corregimientos),
    path('misrutas/cargar-veredas/', rest_views.cargar_veredas),

    path('permisos/autocomplete/usuarios/', rest_views.UsuariosAutocomplete.as_view()),
    path('permisos/autocomplete/rutas/', rest_views.RutasAutocomplete.as_view()),


    #----------------------------------- PERMISOS ------------------------------------

    path('permisos/', rest_views.PermisosListApi.as_view()),
    path('permisos_proyectos/', rest_views.PermisosProyectosListApi.as_view()),


    #----------------------------------- SOPORTES ------------------------------------

    path('soportes/', rest_views.SoportesHogaresListApi.as_view()),
    path('soportes/<uuid:pk_hogar>/', rest_views.SoportesHogaresComponenteListApi.as_view()),
    path('soportes/<uuid:pk_hogar>/componente/<uuid:pk_componente>/', rest_views.SoportesHogaresMomentosListApi.as_view()),
    path('soportes/<uuid:pk_hogar>/componente/<uuid:pk_componente>/instrumento/<uuid:pk_momento>/', rest_views.SoportesHogaresInstrumentosListApi.as_view()),

    #----------------------------------- CORTES ------------------------------------

    path('cortes/', rest_views.CortesListApi.as_view()),
    path('cortes/ver/<uuid:pk_corte>/', rest_views.CortesCuentasCobroListApi.as_view()),

    #------------------------------------ RUTEO -------------------------------------

    path('ruteo/', rest_views.RuteoHogaresListApi.as_view()),
    path('ruteo/<uuid:pk>/componentes/', rest_views.RuteoHogaresComponentesListApi.as_view()),
    path('ruteo/<uuid:pk>/componentes/<uuid:pk_componente>/momentos/', rest_views.RuteoHogaresMomentosListApi.as_view()),


    path('ruteo/autocomplete/rutas/<uuid:pk_componente>/<uuid:pk_ruta>/', rest_views.CambioRutasAutocomplete.as_view()),
    path('ruteo/autocomplete/rutas/<uuid:pk_componente>/', rest_views.CambioRutasAutocompleteAll.as_view()),


    path('ruteo/autocomplete/vinculacion/rutas/<uuid:pk_ruta>/', rest_views.CambioRutasAutocompleteVinculacion.as_view()),
    path('ruteo/autocomplete/vinculacion/rutas/', rest_views.CambioRutasAutocompleteVinculacionAll.as_view()),



    path('directorio/', rest_views.DirectorioListApi.as_view()),


    path('entes_territoriales/', include('entes_territoriales.rest_urls')),


]