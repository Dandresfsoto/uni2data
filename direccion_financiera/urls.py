from django.conf.urls import url
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

    path('enterprise/', views.EnterpriseListView.as_view()),
    path('enterprise/<uuid:pk>/', views.EnterpriseOptionListView.as_view()),


    path('enterprise/<uuid:pk>/projects/', views.EnterpriseProjectsListView.as_view()),
    path('enterprise/<uuid:pk>/projects/crear/', views.EnterpriseProjectsCreateView.as_view()),
    path('enterprise/<uuid:pk>/projects/editar/<uuid:pk_proyecto>/', views.EnterpriseProjectsUpdateView.as_view()),

    path('enterprise/<uuid:pk>/consulta_pagos/', views.ConsultaEnterprisePagosListView.as_view()),
    path('enterprise/<uuid:pk>/consulta_pagos/ver/<uuid:pk_contratista>/', views.ConsultaPagosEnterpriseTerceroListView.as_view()),
    path('enterprise/<uuid:pk>/consulta_pagos/ver/<uuid:pk_contratista>/dinamica/pagos/', views.ConsultaEnterprisePagosTerceroDinamicaListView.as_view()),

    path('enterprise/<uuid:pk>/reportes/informe/', views.InformePagosView.as_view()),
    path('enterprise/<uuid:pk>/reportes/informe_financiero/', views.FinantialReportView.as_view()),
    path('enterprise/<uuid:pk>/reportes/', views.ReportesListView.as_view()),
    path('enterprise/<uuid:pk>/reportes/crear/', views.ReportesCreateView.as_view()),
    path('enterprise/<uuid:pk>/reportes/editar/<uuid:pk_reporte>/', views.ReportesUpdateView.as_view()),
    path('enterprise/<uuid:pk>/reportes/editar/<uuid:pk_reporte>/resultado/', views.ReportesResultadoUpdateView.as_view()),
    path('enterprise/<uuid:pk>/reportes/editar/<uuid:pk_reporte>/reportar/', views.ReporteReportesView.as_view()),
    path('enterprise/<uuid:pk>/reportes/editar/<uuid:pk_reporte>/enviado/', views.ReporteEnvioView.as_view()),
    path('enterprise/<uuid:pk>/reportes/eliminar/<uuid:pk_reporte>/', views.ReportesDeleteView.as_view()),
    path('enterprise/<uuid:pk>/reportes/contabilizar/<uuid:pk_reporte>/', views.ReportesRecordView.as_view()),

    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/', views.PagosListView.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/crear/', views.PagosCreateView.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/editar/<uuid:pk_pago>/', views.PagosUpdateView.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/eliminar/<uuid:pk_pago>/', views.PagosDeleteView.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/amortizaciones/<uuid:pk_pago>/', views.AmortizacionesPagosListView.as_view()),
    path('enterprise/<uuid:pk>/reportes/pagos/<uuid:pk_reporte>/amortizaciones/<uuid:pk_pago>/editar/<uuid:pk_amortizacion>/', views.AmortizacionesPagosUpdateView.as_view()),


    path('enterprise/<uuid:pk>/reporte_eliminado/', views.ReportsRecycleListView.as_view()),
    path('enterprise/<uuid:pk>/reporte_eliminado/restaurar/<uuid:pk_reporte>', views.ReportsRecycleRestoreListView.as_view()),
    path('enterprise/<uuid:pk>/reporte_eliminado/pagos/<uuid:pk_reporte>/', views.PaymentsRecycleListView.as_view()),


    path('enterprise/<uuid:pk>/purchase_order/', views.PurchaseOrderListView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/crear/', views.PurchaseOrderCreateView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/editar/<uuid:pk_purchase>/', views.PurchaseOrderUpdateView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/eliminar/<uuid:pk_purchase>/', views.PurchaseOrderDeleteView.as_view()),

    path('enterprise/<uuid:pk>/purchase_order/products/<uuid:pk_purchase>/', views.ProductsListView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/products/<uuid:pk_purchase>/crear/', views.ProductsCreateView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/products/<uuid:pk_purchase>/editar/<uuid:pk_product>/', views.ProductsUpdateView.as_view()),
    path('enterprise/<uuid:pk>/purchase_order/products/<uuid:pk_purchase>/eliminar/<uuid:pk_product>/', views.ProductsDeleteView.as_view()),

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

    path('collects_account/', views.CollectsAccountListView.as_view()),
    path('collects_account/view/<uuid:pk_cut>/', views.CollectsAccountsView.as_view()),
    path('collects_account/view/<uuid:pk_cut>/upload/<uuid:pk_collect_account>/', views.CollectAccountUploadView.as_view()),
    path('collects_account/view/<uuid:pk_cut>/estate/<uuid:pk_collect_account>/', views.CollectsAccountsEstateView.as_view()),
    path('collects_account/view/<uuid:pk_cut>/estate/<uuid:pk_collect_account>/', views.CollectsAccountsEstateView.as_view()),

]