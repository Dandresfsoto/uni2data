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
]