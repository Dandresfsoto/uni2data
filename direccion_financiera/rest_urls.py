from django.urls import path
from direccion_financiera import rest_views

urlpatterns = [
    path('bancos/', rest_views.BancosListApi.as_view()),

    path('terceros/', rest_views.TercerosListApi.as_view()),

    path('terceros/pagos/<uuid:pk>/', rest_views.TerceroPagosListApi.as_view()),
    path('terceros/pagos/<uuid:pk>/dinamica/pagos/', rest_views.PagosDinamicaAPI.as_view()),


    path('terceros/list/', rest_views.TercerosListApiJson.as_view()),

    path('enterprise/<uuid:pk>/reportes/', rest_views.ReportesListApi.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/', rest_views.PagosListApi.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/amortizaciones/<uuid:pk_pago>/', rest_views.AmortizacionesPagosApi.as_view()),

    path('enterprise/<uuid:pk>/projects/', rest_views.EnterpriseProjectsListApi.as_view()),

    path('enterprise/<uuid:pk>/consulta_pagos/', rest_views.ConsultaEnterprisePagosListApi.as_view()),
    path('enterprise/<uuid:pk>/terceros/pagos/<uuid:pk_contratista>/', rest_views.EnterperiseTerceroPagosListApi.as_view()),
    path('enterprise/<uuid:pk>/terceros/pagos/<uuid:pk_contratista>/dinamica/pagos/', rest_views.EnterprisePagosDinamicaAPI.as_view()),

    path('enterprise/<uuid:pk>/reportes_eliminados/', rest_views.ReportsRecycleListApi.as_view()),
    path('enterprise/<uuid:pk>/reportes_eliminados/pagos/<uuid:pk_reporte>/', rest_views.PaymentsRecycleListApi.as_view()),

    path('terceros/pagos/<uuid:pk>/dinamica/pagos/', rest_views.PagosDinamicaAPI.as_view()),

    path('consulta_pagos/', rest_views.ConsultaPagosListApi.as_view()),

    path('solicitudes_desplazamiento/', rest_views.SolicitudesDesplazamientoListApi.as_view()),
    path('solicitudes_desplazamiento/desplazamientos/<uuid:pk>/', rest_views.DesplazamientosListApi.as_view()),

    path('pagos/<uuid:pk>/', rest_views.PagoApiJson.as_view()),

    path('reportes/cargar-rubro/', rest_views.cargar_rubro),
    path('reportes/cargar-rubro_2/', rest_views.cargar_rubro_2),
    path('reportes/pagos/cargar-contrato/', rest_views.cargar_contrato),
]