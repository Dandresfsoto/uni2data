from django.urls import path
from direccion_financiera import rest_views

urlpatterns = [
    path('bancos/', rest_views.BancosListApi.as_view()),

    path('terceros/', rest_views.TercerosListApi.as_view()),

    path('terceros/pagos/<uuid:pk>/', rest_views.TerceroPagosListApi.as_view()),
    path('terceros/pagos/<uuid:pk>/dinamica/pagos/', rest_views.PagosDinamicaAPI.as_view()),

    path('terceros/list/', rest_views.TercerosListApiJson.as_view()),

    path('reportes/', rest_views.ReportesListApi.as_view()),
    path('reportes/pagos/<uuid:pk>/', rest_views.PagosListApi.as_view()),
    path('reportes/pagos/<uuid:pk>/amortizaciones/<uuid:pk_pago>/', rest_views.AmortizacionesPagosApi.as_view()),

    path('consulta_pagos/', rest_views.ConsultaPagosListApi.as_view()),

    path('solicitudes_desplazamiento/', rest_views.SolicitudesDesplazamientoListApi.as_view()),
    path('solicitudes_desplazamiento/desplazamientos/<uuid:pk>/', rest_views.DesplazamientosListApi.as_view()),

    path('pagos/<uuid:pk>/', rest_views.PagoApiJson.as_view()),
]