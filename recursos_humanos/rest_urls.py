from django.urls import path
from recursos_humanos import rest_views

urlpatterns = [
    path('contratistas/', rest_views.ContratistasListApi.as_view()),
    path('contratistas/contratos/<uuid:pk>/', rest_views.ContratosListApi.as_view()),
    path('contratistas/contratos/<uuid:pk>/otros_si/<uuid:pk_contrato>', rest_views.OtrossiContratoListApi.as_view()),

    path('soportes/tipologia/', rest_views.SoportesListApi.as_view()),
    path('soportes/grupos/', rest_views.GrupoSoportesListApi.as_view()),
    path('contratistas/contratos/<uuid:pk>/soportes/<uuid:pk_soporte>/', rest_views.SoportesContratoListApi.as_view()),
    path('certificaciones/', rest_views.CertificacionesListApi.as_view()),
    path('certificaciones/cedula/', rest_views.CertificacionesCedulaApi.as_view()),
    path('hv/', rest_views.HvListApi.as_view()),
    path('hv/trazabilidad/<uuid:pk>/', rest_views.HvTrazabilidadApiJson.as_view()),

    path('hv/autocomplete/contratistas/',rest_views.ContratistaAutocomplete.as_view()),
    path('contratos/', rest_views.ContratosEstadoListApi.as_view()),

    path('cuts/', rest_views.CutsListApi.as_view()),
    path('cuts/view/<uuid:pk_cut>/', rest_views.CutsCollectAccountListApi.as_view()),

    path('liquidations/', rest_views.LiquidationsListApi.as_view()),

    path('cargos/', rest_views.CargosListApi.as_view()),
]