from django.urls import path, include
from fest_2019 import views

urlpatterns = [
    path('', views.Fest2019OptionsView.as_view()),


    path('migeoreferenciacion/', views.MiGeoreferenciacionListView.as_view()),
    path('georeferenciacion/', views.GeoreferenciacionListView.as_view()),
    path('georeferenciacion/informe/', views.InformeGeoreferenciacionView.as_view()),

    path('misproyectos/', views.MisProyectosListView.as_view()),
    path('misproyectos/editar/<int:pk>/', views.MisProyectosUpdateView.as_view()),
    path('misproyectos/estado/<int:pk>/', views.MisProyectosEstadoView.as_view()),
    path('misproyectos/hogares/<int:pk>/', views.MisProyectosHogaresView.as_view()),
    path('misproyectos/flujo/<int:pk>/', views.MisProyectosFlujoUpdateView.as_view()),
    path('misproyectos/identificacion/<int:pk>/', views.MisProyectosIdentificacionUpdateView.as_view()),
    path('misproyectos/observaciones/<int:pk>/', views.MisProyectosObservacionesView.as_view()),



    path('proyectos_local/', views.ProyectosLocalListView.as_view()),
    path('proyectos_local/editar/<int:pk>/', views.ProyectosLocalUpdateView.as_view()),
    path('proyectos_local/flujo/<int:pk>/', views.ProyectosLocalFlujoUpdateView.as_view()),
    path('proyectos_local/identificacion/<int:pk>/', views.ProyectosLocalIdentificacionUpdateView.as_view()),
    path('proyectos_local/estado/<int:pk>/', views.ProyectosLocalVerificarView.as_view()),
    path('proyectos_local/hogares/<int:pk>/', views.ProyectosLocalHogaresView.as_view()),
    path('proyectos_local/observaciones/<int:pk>/', views.ProyectosLocalObservacionesView.as_view()),


    path('proyectos_monitoreo/', views.ProyectosMonitoreoListView.as_view()),
    path('proyectos_monitoreo/editar/<int:pk>/', views.ProyectosMonitoreoUpdateView.as_view()),
    path('proyectos_monitoreo/flujo/<int:pk>/', views.ProyectosMonitoreoFlujoUpdateView.as_view()),
    path('proyectos_monitoreo/identificacion/<int:pk>/', views.ProyectosMonitoreoIdentificacionUpdateView.as_view()),
    path('proyectos_monitoreo/observaciones/<int:pk>/', views.ProyectosMonitoreoObservacionesView.as_view()),
    path('proyectos_monitoreo/estado/<int:pk>/', views.ProyectosMonitoreoEstadoView.as_view()),
    path('proyectos_monitoreo/hogares/<int:pk>/', views.ProyectosMonitoreoHogaresView.as_view()),


    path('proyectos_especialistas/', views.ProyectosEspecialistasListView.as_view()),
    path('proyectos_especialistas/editar/<int:pk>/', views.ProyectosEspecialistasUpdateView.as_view()),
    path('proyectos_especialistas/flujo/<int:pk>/', views.ProyectosEspecialistasFlujoUpdateView.as_view()),
    path('proyectos_especialistas/identificacion/<int:pk>/', views.ProyectosEspecialistasIdentificacionUpdateView.as_view()),
    path('proyectos_especialistas/observaciones/<int:pk>/', views.ProyectosEspecialistasObservacionesView.as_view()),
    path('proyectos_especialistas/estado/<int:pk>/', views.ProyectosEspecialistasEstadoView.as_view()),
    path('proyectos_especialistas/hogares/<int:pk>/', views.ProyectosEspecialistasHogaresView.as_view()),


    path('bd/', views.HogaresListView.as_view()),
    path('bd/crear/', views.HogaresCreateView.as_view()),
    path('bd/editar/<uuid:pk>/', views.HogaresUpdateView.as_view()),

    path('entregables/', views.EntregablesListView.as_view()),
    path('entregables/informe_actividades/', views.InformeActividadesListView.as_view()),
    path('entregables/<uuid:pk_componente>/momentos/', views.VisitasListView.as_view()),
    path('entregables/<uuid:pk_componente>/momentos/<uuid:pk_momento>/instrumentos/', views.InstrumentosListView.as_view()),
    path('entregables/<uuid:pk_componente>/momentos/<uuid:pk_momento>/instrumentos/informe/<uuid:pk_instrumento>/', views.InstrumentosInformeListView.as_view()),



    path('entes_territoriales/', include('entes_territoriales.urls')),




    #------------------------------------- RUTAS -------------------------------------
    #Gestión de rutas
    path('rutas/', views.RutasListView.as_view()),  #Permisos revisados
    path('rutas/crear/', views.RutasCreateView.as_view()),  #Permisos revisados
    path('rutas/editar/<uuid:pk_ruta>/', views.RutasUpdateView.as_view()),  #Permisos revisados


    #Gestión de hogares
    path('rutas/hogares/<uuid:pk_ruta>/', views.RutasHogaresListView.as_view()),    #Permisos revisados
    path('rutas/hogares/<uuid:pk_ruta>/crear/', views.RutaCrearHogarView.as_view()),    #Permisos revisados
    path('rutas/hogares/<uuid:pk_ruta>/ver/<uuid:pk_hogar>/', views.RutasHogaresVerView.as_view()), #Permisos revisados


    path('rutas/actividades/<uuid:pk_ruta>/', views.RutasActividadesListView.as_view()), #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/valores/', views.RutasActividadesValoresView.as_view()),


    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/', views.RutasInstrumentosHogaresListView.as_view()),     #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/agregar/<uuid:pk_instrumento>/', views.RutasInstrumentosFormHogaresListView.as_view()),
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/eliminar/<uuid:pk_instrumento_object>/', views.RutasInstrumentosHogaresDeleteView.as_view()),
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/ver/<uuid:pk_instrumento_object>/', views.RutasInstrumentosVerHogaresView.as_view()), #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/trazabilidad/<uuid:pk_instrumento_object>/', views.RutasInstrumentosTrazabilidadHogaresView.as_view()),   #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/editar/<uuid:pk_instrumento_object>/', views.RutasInstrumentosUpdateHogaresListView.as_view()),


    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/aprobar/<uuid:pk_instrumento_object>/', views.AprobarInstrumentoHogaresView.as_view()),   #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/rechazar/<uuid:pk_instrumento_object>/', views.RutasInstrumentosRechazarHogaresView.as_view()),   #Permisos revisados


    #------------------------------------- CUENTAS DE COBRO -------------------------------------
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/', views.RutasCuentasCobroListView.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', views.RutasCuentasCobroDetalleListView.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/', views.RutasCuentasCobroDetalleActividadesListView.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/', views.RutasCuentasCobroInstrumentosHogaresListView.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/ver/<uuid:pk_instrumento_object>/', views.RutasCuentasCobroInstrumentosVerHogaresView.as_view()),
    path('rutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/trazabilidad/<uuid:pk_instrumento_object>/', views.RutasCuentasCobroInstrumentosTrazabilidadHogaresView.as_view()),







    #path('rutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/', views.RutasHogaresMiembrosListView.as_view()),
    #path('rutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/ver/<uuid:pk_miembro>/', views.RutasHogaresMiembrosVerView.as_view()),


    #path('rutas/hogares/<uuid:pk_ruta>/cargar/', views.RutasHogaresCreateView.as_view()),


    #Gestión de actividades




    #path('rutas/actividades/<uuid:pk_ruta>/objetos/<uuid:pk_momento>/', views.RutasActividadesListObjetosView.as_view()),

    #path('rutas/actividades/<uuid:pk_ruta>/objetos/<uuid:pk_momento>/cero/<uuid:pk_cupo>/', views.RutasActividadesObjeroCeroView.as_view()),





    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/', views.RutasActividadesHogaresListView.as_view()),   #Permisos revisados



    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/aprobar/', views.RutasInstrumentoHogarAprobarView.as_view()),
    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/rechazar/', views.RutasInstrumentoHogarRechazarView.as_view()),






    #path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/preaprobar/<uuid:pk_instrumento_object>/', views.RutasInstrumentosPreaprobarHogaresView.as_view()),   #Permisos revisados
    path('rutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/rechazar/<uuid:pk_instrumento_object>/', views.RutasInstrumentosRechazarHogaresView.as_view()),   #Permisos revisados

    #----------------------------------- MIS RUTAS ------------------------------------

    path('misrutas/', views.MisRutasOptionsView.as_view()),
    path('misrutas/hogares/<uuid:pk_ruta>/', views.MisRutasHogaresListView.as_view()),
    path('misrutas/hogares/<uuid:pk_ruta>/crear/', views.RutaCrearMisHogaresView.as_view()),    #Permisos revisados
    path('misrutas/hogares/<uuid:pk_ruta>/ver/<uuid:pk_hogar>/', views.MisRutasHogaresVerView.as_view()),


    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/', views.MisRutasInstrumentosHogaresListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/agregar/<uuid:pk_instrumento>/', views.MisRutasInstrumentosFormHogaresListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/editar/<uuid:pk_instrumento_object>/', views.MisRutasInstrumentosUpdateHogaresListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/ver/<uuid:pk_instrumento_object>/', views.MisRutasInstrumentosVerHogaresView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/observaciones/<uuid:pk_instrumento_object>/', views.MisRutasInstrumentosHogaresObservacionesListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/instrumentos/<uuid:pk_momento>/eliminar/<uuid:pk_instrumento_object>/', views.MisRutasInstrumentosHogaresDeleteView.as_view()),


    #path('misrutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/', views.MisRutasHogaresMiembrosListView.as_view()),
    #path('misrutas/hogares/<uuid:pk_ruta>/ver_miembros/<uuid:pk_hogar>/ver/<uuid:pk_miembro>/', views.MisRutasHogaresMiembrosVerView.as_view()),
    #path('misrutas/hogares/<uuid:pk_ruta>/agregar_miembro/<uuid:pk_hogar>/', views.MisRutasHogaresAgregarMiembroListView.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/', views.MisRutasActividadesListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/hogares/<uuid:pk_momento>/', views.MisRutasActividadesHogaresListView.as_view()),









    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/', views.MisRutasCuentasCobroListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/cargar/<uuid:pk_cuenta_cobro>/', views.MisRutasCuentasCobroUploadView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', views.MisRutasCuentasCobroDetalleListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/', views.MisRutasCuentasCobroDetalleActividadesListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/', views.MisRutasCuentasCobroInstrumentosHogaresListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/ver/<uuid:pk_instrumento_object>/', views.MisRutasCuentasCobroInstrumentosVerHogaresView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/hogares/<uuid:pk_momento>/instrumentos/<uuid:pk_hogar>/trazabilidad/<uuid:pk_instrumento_object>/', views.MisRutasCuentasCobroInstrumentosTrazabilidadHogaresView.as_view()),




    #------------------------------------- PERMISOS -------------------------------------

    path('permisos/', views.PermisosListView.as_view()),
    path('permisos/crear/', views.PermisosCreateView.as_view()),
    path('permisos/editar/<uuid:pk>/', views.PermisosUpdateView.as_view()),


#------------------------------------- PERMISOS -------------------------------------

    path('permisos_proyectos/', views.PermisosProyectosListView.as_view()),
    path('permisos_proyectos/crear/', views.PermisosProyectosCreateView.as_view()),
    path('permisos_proyectos/editar/<uuid:pk>/', views.PermisosProyectosUpdateView.as_view()),


    #------------------------------------- SOPORTES -------------------------------------

    path('soportes/', views.SoportesHogaresListView.as_view()),
    path('soportes/<uuid:pk_hogar>/', views.SoportesHogaresComponenteListView.as_view()),
    path('soportes/<uuid:pk_hogar>/componente/<uuid:pk_componente>/', views.SoportesHogaresMomentosListView.as_view()),
    path('soportes/<uuid:pk_hogar>/componente/<uuid:pk_componente>/instrumento/<uuid:pk_momento>/', views.SoportesHogaresInstrumentosListView.as_view()),
    path('soportes/<uuid:pk_hogar>/componente/<uuid:pk_componente>/instrumento/<uuid:pk_momento>/ver/<uuid:pk_instrumento_object>/', views.SoportesHogaresInstrumentosVerView.as_view()),


    #------------------------------------- CORTES -------------------------------------

    path('cortes/', views.CortesListView.as_view()),
    path('cortes/crear/', views.CortesCreateView.as_view()),
    path('cortes/ver/<uuid:pk_corte>/', views.CortesCuentasCobroView.as_view()),
    path('cortes/ver/<uuid:pk_corte>/editar/<uuid:pk_cuenta_cobro>/', views.CuentaCobroUpdateView.as_view()),
    path('cortes/ver/<uuid:pk_corte>/cargar/<uuid:pk_cuenta_cobro>/', views.CuentaCobroFirmaUploadView.as_view()),
    path('cortes/ver/<uuid:pk_corte>/estado/<uuid:pk_cuenta_cobro>/', views.CuentaCobroEstadoFormView.as_view()),

    #---------------------------------------RUTEO--------------------------------------

    path('ruteo/', views.RuteoHogaresListView.as_view()),
    path('ruteo/reportes/ruteo/', views.RuteoHogaresReporteListadoView.as_view()),

    path('ruteo/<uuid:pk>/cambiar/vinculacion/', views.RuteoHogaresComponentesVinculacionView.as_view()),

    path('ruteo/<uuid:pk>/componentes/', views.RuteoHogaresComponentesListView.as_view()),
    path('ruteo/<uuid:pk>/componentes/<uuid:pk_componente>/cambiar/componente/', views.RuteoHogaresComponentesCambiarView.as_view()),
    path('ruteo/<uuid:pk>/componentes/<uuid:pk_componente>/momentos/', views.RuteoHogaresMomentosListView.as_view()),


    #---------------------------------------RUTEO--------------------------------------

    path('directorio/', views.DirectorioListView.as_view()),
    path('directorio/crear/', views.DirectorioCreateView.as_view()),
    path('directorio/editar/<uuid:pk>/', views.DirectorioUpdateView.as_view()),


]


