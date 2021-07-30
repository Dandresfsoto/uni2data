from django.urls import path, include
from cpe_2018 import views

urlpatterns = [
    path('', views.Cpe2018OptionsView.as_view()),


    path('informes/', views.InformesListView.as_view()),
    path('informes/<uuid:pk>/', views.InformesRegionListView.as_view()),
    path('informes/<uuid:pk>/matricula/', views.InformeMatriculaRegionListView.as_view()),
    path('informes/<uuid:pk>/sedes/', views.InformeSedesRegionListView.as_view()),
    path('informes/<uuid:pk>/retoma/', views.InformeRetomaRegionListView.as_view()),
    path('informes/<uuid:pk>/formacion/', views.InformeFormacionRegionListView.as_view()),


    path('soportes/', views.SoportesListView.as_view()),
    path('soportes/<uuid:pk>/', views.SoportesRegionListView.as_view()),

    path('soportes/<uuid:pk>/sedes/', views.SoportesSedesListView.as_view()),
    path('soportes/<uuid:pk>/sedes/ver/<uuid:pk_radicado>/', views.SoportesVerSedesListView.as_view()),

    path('soportes/<uuid:pk>/docentes/', views.SoportesDocentesListView.as_view()),
    path('soportes/<uuid:pk>/docentes/ver/<uuid:pk_docente>/', views.SoportesVerDocentesListView.as_view()),


    path('soportes/<uuid:pk>/retomas/', views.SoportesRetomasListView.as_view()),


    path('bd/', views.RegionesListView.as_view()),
    path('bd/actualizar/', views.ActualizacionDbListView.as_view()),
    path('bd/actualizar_docentes/', views.ActualizacionDbDocentesListView.as_view()),
    path('bd/actualizar/nuevo/', views.CreateActualizacionDbView.as_view()),
    path('bd/actualizar_docentes/nuevo/', views.CreateActualizacionDbDocentesView.as_view()),


    path('bd/<uuid:pk>/departamentos/', views.DepartamentosListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/', views.MunicipiosListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/radicados/', views.RadicadosListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/docentes/', views.DocentesListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/radicados/crear/', views.RadicadosCreateView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/radicados/editar/<uuid:pk_radicado>/', views.RadicadosUpdateView.as_view()),


    path('componentes/', views.ComponentesListView.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/', views.EstrategiasListView.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/<uuid:pk_estrategia>/momentos/', views.MomentosListView.as_view()),
    path('componentes/<uuid:pk_componente>/estrategias/<uuid:pk_estrategia>/momentos/<uuid:pk_momento>/entregables/', views.EntregablesListView.as_view()),
    #path('formacion/', include('formacion.urls')),
    #path('acceso/', include('acceso.urls')),


    path('entes_territoriales/', include('entes_territoriales.urls')),
    path('solicitudes_desplazamiento/', include('desplazamiento.urls')),
    path('formatos/', include('formatos.urls')),



    #------------------------------------- RUTAS -------------------------------------

    path('rutas/', views.RutasOptionsView.as_view()),
    path('rutas/<uuid:pk>/', views.RutasRegionListView.as_view()),
    path('rutas/<uuid:pk>/crear/', views.RutasRegionCreateView.as_view()),
    path('rutas/<uuid:pk>/editar/<uuid:pk_ruta>/', views.RutasRegionUpdateView.as_view()),
    path('rutas/<uuid:pk>/editar/<uuid:pk_ruta>/estado/', views.RutasRegionEstadoView.as_view()),
    path('rutas/<uuid:pk>/reportes/ruteo/', views.ReportesRuteoView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/', views.ComponentesRutasListView.as_view()),


    #--------------------------------- CUENTAS COBRO ----------------------------------

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/', views.RutasCuentasCobroListView.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', views.RutasCuentasCobroDetalleListView.as_view()),

    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/', views.RutasCuentasCobroDetalleComponenteListView.as_view()),


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/', views.RutasCuentasCobroDetalleRetomaListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/', views.RutasCuentasCobroDetalleVerRetomaListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/trazabilidad/', views.RutasCuentasCobroDetalleVerRetomaTrazabilidadListView.as_view()),


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', views.ActividadesSedeRutaCuentaCobroListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeRutaCuentaCobroVerView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeRutaCuentaCobroRutaVerView.as_view()),


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', views.RutasCuentasCobroDetalleRadicadoListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', views.RutasCuentasCobroDetalleRadicadoSoportesListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeCuentaCobroVerView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeCuentaCobroRutaVerView.as_view()),


    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/', views.FormacionRutaCuentaCobroListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/', views.DocentesActividadesRutaCuentaCobroListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', views.DocentesActividadesEntregablesRutaCuentaCobroListView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/', views.DocentesActividadesEntregablesRutaVerCuentaCobroView.as_view()),
    path('rutas/<uuid:pk>/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/trazabilidad/', views.TrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView.as_view()),

    #------------------------------------- ACCESO -------------------------------------

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/', views.ActividadesComponenteRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/toogle/<uuid:pk_entregable_ruta_object>/', views.ToogleActividadesComponenteRutaListView.as_view()),


    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/', views.ActividadesRetomaRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/verificar/<uuid:pk_retoma>/', views.VerificarRetomaRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/crear/', views.RetomaRutaCreateListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/editar/<uuid:pk_retoma>/', views.RetomaRutaUpdateListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/eliminar/<uuid:pk_retoma>/', views.RetomaRutaDeleteListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/', views.RetomaRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/trazabilidad/', views.TrazabilidadRetomaRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/calificar/', views.CalificarRetomaRutaView.as_view()),


    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', views.ActividadesSedeRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/crear/', views.ActividadesSedeRutaCreateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/editar/<uuid:pk_soporte>/', views.ActividadesSedeRutaUpdateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/eliminar/<uuid:pk_soporte>/', views.ActividadesSedeRutaDeleteListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/calificar/', views.CalificarSedeRutaVerView.as_view()),


    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', views.ActividadesComponenteRutaRadicadoListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/toogle/<uuid:pk_entregable_ruta_object>/', views.ToogleActividadesComponenteRutaRadicadoListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', views.ActividadesSedeListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/crear/', views.ActividadesSedeCreateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/editar/<uuid:pk_soporte>/', views.ActividadesSedeUpdateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/eliminar/<uuid:pk_soporte>/', views.ActividadesSedeDeleteListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/calificar/', views.CalificarSedeVerView.as_view()),

    #----------------------------------------------------------------------------------

    #----------------------------------- FORMACIÓN ------------------------------------

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/', views.FormacionRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/crear/', views.FormacionRutaCreateGroupView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/editar/<uuid:pk_grupo>/', views.FormacionRutaUpdateGroupView.as_view()),

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/', views.DocentesGrupoRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/retirar/<uuid:pk_docente>/', views.DocentesRetirarRutaListView.as_view()),

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/verificar/<uuid:pk_docente>/', views.VerificarDocentesGrupoRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/agregar/', views.AgregarDocenteGrupoRutaListView.as_view()),

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/', views.DocentesActividadesRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/liquidacion/<uuid:pk_entregable>/', views.DocentesLiquidacionRutaListView.as_view()),

    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', views.DocentesActividadesEntregablesRutaListView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/crear/', views.DocentesActividadesEntregablesRutaCreateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/editar/<uuid:pk_objeto>/', views.DocentesActividadesEntregablesRutaUpdateView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/eliminar/<uuid:pk_objeto>/', views.DocentesActividadesEntregablesRutaDeleteView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/', views.DocentesActividadesEntregablesRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/trazabilidad/', views.TrazabilidadDocentesActividadesEntregablesRutaVerView.as_view()),
    path('rutas/<uuid:pk>/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/calificar/', views.CalificarDocentesActividadesEntregablesRutaView.as_view()),

    #----------------------------------------------------------------------------------

    #----------------------------------- MIS RUTAS ------------------------------------

    path('misrutas/', views.MisRutasOptionsView.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/', views.ComponentesMisRutasListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/', views.ActividadesComponenteMisRutasListView.as_view()),

    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/', views.ActividadesRetomaMisRutasListView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/', views.RetomaMisRutasVerView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/trazabilidad/', views.TrazabilidadRetomaMisRutasVerView.as_view()),


    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', views.ActividadesSedeMisRutasListView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeMisRutasVerView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeMisRutasVerView.as_view()),


    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', views.ActividadesComponenteMisRutasRadicadoListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', views.ActividadesMisRutasSedeListView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesRadicadoSedeMisRutasVerView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeMisrutasRadicadoVerView.as_view()),


    path('misrutas/actividades/<uuid:pk_ruta>/formacion/', views.FormacionMisRutasListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/docentes/<uuid:pk_grupo>/', views.DocentesGrupoMisRutasListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/', views.DocentesActividadesMisRutasListView.as_view()),
    path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', views.DocentesActividadesEntregablesMisRutasListView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/', views.DocentesActividadesEntregablesMisRutasVerView.as_view()),
    #path('misrutas/actividades/<uuid:pk_ruta>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/trazabilidad/', views.TrazabilidadDocentesActividadesEntregablesMisRutasVerView.as_view()),




    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/', views.MisRutasCuentasCobroListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/cargar/<uuid:pk_cuenta_cobro>/', views.MisRutasCuentasCobroUploadView.as_view()),

    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/', views.MisRutasCuentasCobroDetalleListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/', views.MisRutasCuentasCobroDetalleComponenteListView.as_view()),


    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/', views.MisRutasCuentasCobroDetalleRetomaListView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/', views.MisRutasCuentasCobroDetalleVerRetomaListView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/retoma/ver/<uuid:pk_retoma>/trazabilidad/', views.MisRutasCuentasCobroDetalleVerRetomaTrazabilidadListView.as_view()),


    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/', views.ActividadesSedeMisRutasCuentaCobroListView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.ActividadesSedeMisRutaCuentaCobroVerView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.TrazabilidadSedeRutaCuentaCobroMisRutasVerView.as_view()),


    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/', views.MisRutasCuentasCobroDetalleRadicadoListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/', views.MisRutasCuentasCobroDetalleRadicadoSoportesListView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/', views.MisActividadesSedeCuentaCobroVerView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/componente/<uuid:pk_componente>/radicado/<uuid:pk_radicado>/cargar/<uuid:pk_objeto>/ver/<uuid:pk_soporte>/trazabilidad/', views.MisTrazabilidadSedeCuentaCobroRutaVerView.as_view()),


    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/', views.MiFormacionRutaCuentaCobroListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/', views.MisDocentesActividadesRutaCuentaCobroListView.as_view()),
    path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/', views.MisDocentesActividadesEntregablesRutaCuentaCobroListView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/', views.MisDocentesActividadesEntregablesRutaVerCuentaCobroView.as_view()),
    #path('misrutas/cuentas_cobro/<uuid:pk_ruta>/detalle/<uuid:pk_cuenta_cobro>/formacion/actividades/<uuid:pk_grupo>/evidencias/<uuid:pk_entregable>/ver/<uuid:pk_objeto>/trazabilidad/', views.MisTrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView.as_view()),



    #----------------------------------------------------------------------------------

    #----------------------------------- MIS RUTAS ------------------------------------

    path('cortes/', views.CortesOptionsView.as_view()),
    path('cortes/<uuid:pk>/', views.CortesRegionListView.as_view()),
    path('cortes/<uuid:pk>/crear/', views.CortesRegionCreateView.as_view()),
    path('cortes/<uuid:pk>/ver/<uuid:pk_corte>/', views.CortesRegionCuentasCobroView.as_view()),
    path('cortes/<uuid:pk>/ver/<uuid:pk_corte>/editar/<uuid:pk_cuenta_cobro>/', views.CuentaCobroUpdateView.as_view()),
    path('cortes/<uuid:pk>/ver/<uuid:pk_corte>/cargar/<uuid:pk_cuenta_cobro>/', views.CuentaCobroFirmaUploadView.as_view()),
    path('cortes/<uuid:pk>/ver/<uuid:pk_corte>/estado/<uuid:pk_cuenta_cobro>/', views.CuentaCobroEstadoFormView.as_view()),

    #----------------------------------------------------------------------------------

    #-------------------------------------- REDS --------------------------------------

    path('red/', views.RedsOptionsView.as_view()),

    path('red/<uuid:pk>/', views.RedsRegionListView.as_view()),
    path('red/<uuid:pk>/tablero_control/', views.ReporteTableroControlView.as_view()),

    path('red/<uuid:pk>/crear/', views.RedsRegionCreateView.as_view()),
    path('red/<uuid:pk>/informe/', views.RedsRegionInformeView.as_view()),
    path('red/<uuid:pk>/editar/<uuid:pk_red>/', views.RedsRegionUpdateView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/', views.RedsRegionVerView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/estado_revision/', views.ReporteEstadoRevisionRedView.as_view()),

    path('red/<uuid:pk>/ver/<uuid:pk_red>/actividades/<uuid:pk_entregable>/', views.RedsRegionVerActividadesView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/actividades/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/', views.RedsRegionActividadCalificarView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/actividades/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/activar/', views.RedsRegionActividadCalificarActivarView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/actividades/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/observaciones/', views.RedsRegionActividadObservacionesView.as_view()),

    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/', views.RedsRegionVerActividadesEstrategiaView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/calificar/<uuid:pk_entregable>/', views.RedsRegionVerActividadesFormacionView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/calificar/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/', views.RedsRegionActividadCalificarFormacionView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/calificar/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/observaciones/', views.RedsRegionActividadObservacionesFormacionView.as_view()),
    path('red/<uuid:pk>/ver/<uuid:pk_red>/formacion/<uuid:pk_estrategia>/calificar/<uuid:pk_entregable>/calificar/<uuid:pk_soporte>/activar/', views.RedsRegionActividadActivarFormacionView.as_view()),



    path('liquidaciones/', views.LiquidacionesOptionsView.as_view()),
    path('liquidaciones/<uuid:pk>/', views.LiquidacionesRutasRegionListView.as_view()),
    path('liquidaciones/<uuid:pk>/generar/<uuid:pk_ruta>/', views.LiquidacionRutaRegionView.as_view()),
    path('liquidaciones/<uuid:pk>/estado/<uuid:pk_liquidacion>/', views.LiquidacionEstadoFormView.as_view()),


    #----------------------------------------------------------------------------------
]