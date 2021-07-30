from django.urls import path
from direccion_financiera import views

urlpatterns = [
    path('', views.DireccionFinancieraOptionsView.as_view()),

    path('bancos/', views.BancosListView.as_view()),
    path('bancos/crear/', views.BancosCreateView.as_view()),
    path('bancos/editar/<uuid:pk>/', views.BancosUpdateView.as_view()),

    path('terceros/', views.TercerosListView.as_view()),
    path('terceros/reportes/listado/', views.TercerosReporteListadoView.as_view()),
    path('terceros/pagos/<uuid:pk>/', views.TercerosTerceroPagosListView.as_view()),
    path('terceros/pagos/<uuid:pk>/reportes/pagos/', views.TerceroPagosReporteView.as_view()),
    path('terceros/pagos/<uuid:pk>/dinamica/pagos/', views.TerceroPagosDinamicaView.as_view()),
    path('terceros/crear/', views.TercerosCreateView.as_view()),
    path('terceros/editar/<uuid:pk>/', views.TercerosUpdateView.as_view()),

    path('reportes/', views.ReportesListView.as_view()),
    path('reportes/informe/', views.InformePagosView.as_view()),
    path('reportes/crear/', views.ReportesCreateView.as_view()),
    path('reportes/editar/<uuid:pk>/', views.ReportesUpdateView.as_view()),
    path('reportes/editar/<uuid:pk>/resultado/', views.ReportesResultadoUpdateView.as_view()),
    path('reportes/editar/<uuid:pk>/reportar/', views.ReporteReportesView.as_view()),
    path('reportes/editar/<uuid:pk>/enviado/', views.ReporteEnvioView.as_view()),
    path('reportes/eliminar/<uuid:pk>/', views.ReportesDeleteView.as_view()),

    path('reportes/pagos/<uuid:pk>/', views.PagosListView.as_view()),
    path('reportes/pagos/<uuid:pk>/crear/', views.PagosCreateView.as_view()),
    path('reportes/pagos/<uuid:pk>/editar/<uuid:pk_pago>/', views.PagosUpdateView.as_view()),
    path('reportes/pagos/<uuid:pk>/eliminar/<uuid:pk_pago>/', views.PagosDeleteView.as_view()),
    path('reportes/pagos/<uuid:pk>/amortizaciones/<uuid:pk_pago>/', views.AmortizacionesPagosListView.as_view()),
    path('reportes/pagos/<uuid:pk>/amortizaciones/<uuid:pk_pago>/editar/<uuid:pk_amortizacion>/', views.AmortizacionesPagosUpdateView.as_view()),

    path('consulta_pagos/', views.ConsultaPagosListView.as_view()),
    path('consulta_pagos/ver/<uuid:pk>/', views.ConsultaPagosTerceroListView.as_view()),
    path('consulta_pagos/ver/<uuid:pk>/dinamica/pagos/', views.ConsultaPagosTerceroDinamicaListView.as_view()),

    path('solicitudes_desplazamiento/', views.SolicitudesDesplazamientoListView.as_view()),
    path('solicitudes_desplazamiento/reporte/', views.SolicitudesDesplazamientoReporteView.as_view()),

    path('solicitudes_desplazamiento/<uuid:pk>/estado/', views.UpdateEstadoSolicitudView.as_view()),

    path('solicitudes_desplazamiento/editar/<uuid:pk>/', views.ListaDesplazamientosView.as_view()),
    path('solicitudes_desplazamiento/editar/<uuid:pk>/editar/<uuid:pk_desplazamiento>/', views.DesplazamientosUpdateView.as_view()),
    path('solicitudes_desplazamiento/editar/<uuid:pk>/eliminar/<uuid:pk_desplazamiento>/', views.DesplazamientosDeleteView.as_view()),

    path('solicitudes_desplazamiento/editar/<uuid:pk>/aprobar/', views.DesplazamientosAprobarView.as_view()),
    path('solicitudes_desplazamiento/editar/<uuid:pk>/rechazar/', views.DesplazamientosRechazarView.as_view()),
]