from django.urls import path
from entes_territoriales import rest_views

urlpatterns = [
    path('reuniones/', rest_views.ReunionesListApi.as_view()),
    path('reuniones/<uuid:pk>/contactos/', rest_views.ReunionesContactosListApi.as_view()),
    path('reuniones/<uuid:pk>/contactos/<uuid:pk_contacto>/soportes/', rest_views.ReunionesContactosSoportesListApi.as_view()),
    path('reuniones/<uuid:pk>/hitos/', rest_views.ReunionesHitosListApi.as_view()),

    path('reuniones/<uuid:pk>/hitos/<uuid:pk_hito>/api_foto/<int:int_foto>/', rest_views.FotosHitosApi.as_view()),

    path('reuniones/autocomplete/municipios/', rest_views.MunicipiosAutocomplete.as_view()),
]