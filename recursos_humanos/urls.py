from django.urls import path
from recursos_humanos import views

urlpatterns = [
    path('', views.RhoptionsView.as_view()),

    path('contratistas/', views.ContratistasListView.as_view()),
    path('contratistas/crear/', views.ContratistasCreateView.as_view()),
    path('contratistas/editar/<uuid:pk>/', views.ContratistasUpdateView.as_view()),
    path('contratistas/editar/<uuid:pk>/certificacion/', views.CertificacionesCreateView.as_view()),


    path('contratistas/contratos/<uuid:pk>/', views.ContratosListView.as_view()),
    path('contratistas/contratos/<uuid:pk>/crear/', views.ContratosCreateView.as_view()),
    path('contratistas/contratos/<uuid:pk>/editar/<uuid:pk_contrato>/', views.ContratosUpdateView.as_view()),


    path('contratistas/contratos/<uuid:pk>/soportes/<uuid:pk_soporte>/', views.ContratosSoportesListView.as_view()),
    path('contratistas/contratos/<uuid:pk>/soportes/<uuid:pk_soporte>/crear/', views.ContratosSoportesCreateView.as_view()),
    path('contratistas/contratos/<uuid:pk>/soportes/<uuid:pk_soporte>/editar/<uuid:pk_soporte_contrato>/', views.ContratosSoportesUpdateView.as_view()),

    path('soportes/tipologia/', views.SoportesListView.as_view()),
    path('soportes/tipologia/crear/', views.SoportesCreateView.as_view()),
    path('soportes/tipologia/editar/<uuid:pk>/', views.SoportesUpdateView.as_view()),

    path('soportes/grupos/', views.GruposSoportesListView.as_view()),
    path('soportes/grupos/crear/', views.GruposSoportesCreateView.as_view()),
    path('soportes/grupos/editar/<uuid:pk>/', views.GruposSoportesUpdateView.as_view()),

    path('certificaciones/', views.CertificacionesListView.as_view()),
    path('certificaciones/editar/<int:pk>/', views.CertificacionesUpdateView.as_view()),

    path('hv/', views.HvListView.as_view()),
    path('hv/crear/', views.HvCreateView.as_view()),
    path('hv/editar/<uuid:pk>/', views.HvUpdateView.as_view()),
    path('hv/<uuid:pk>/estado/', views.HvEstadoView.as_view()),

    path('contratos/', views.ContratosEstadoListView.as_view()),
    path('contratos/editar/<uuid:pk_contrato>/', views.ContratosEstadoUpdateView.as_view()),

    path('contratos/soportes/<uuid:pk_soporte>/', views.ContratosEstadoSoportesListView.as_view()),
    path('contratos/soportes/<uuid:pk_soporte>/editar/<uuid:pk_soporte_contrato>/', views.ContratosEstadoSoportesUpdateView.as_view()),

    path('contratos/reportes/listado/', views.ContratosReporteListadoView.as_view()),
    path('hv/reporte/', views.HvReporteView.as_view()),


    path('cuts/', views.CutsListView.as_view()),
    path('cuts/create/', views.CutsCreateView.as_view()),
    path('cuts/view/<uuid:pk_cut>/', views.CutsCollectsAccountView.as_view()),
    path('cuts/view/<uuid:pk_cut>/add/', views.CutsCollectsAddAccountView.as_view()),
    path('cuts/view/<uuid:pk_cut>/edit/<uuid:pk_collect_account>/', views.CollectAccountUpdateView.as_view()),
    path('cuts/view/<uuid:pk_cut>/upload/<uuid:pk_collect_account>/', views.CollectAccountUploadView.as_view()),
    path('cuts/view/<uuid:pk_cut>/aprobar/<uuid:pk_collect_account>/', views.CollectAccountApprobView.as_view()),
    path('cuts/view/<uuid:pk_cut>/rechazar/<uuid:pk_collect_account>/', views.CollectAccountRejectView.as_view()),
    path('cuts/view/<uuid:pk_cut>/delete/<uuid:pk_collect_account>/', views.CollectAccountDeleteView.as_view()),
]