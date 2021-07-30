from django.urls import path
from formacion import rest_views

urlpatterns = [
    path('bd/', rest_views.RegionesListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/', rest_views.DepartamentosListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/', rest_views.MunicipiosListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/', rest_views.SedesListApi.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/<uuid:pk_sede>/formados/', rest_views.FormadosListApi.as_view()),

    path('db/actualizar/', rest_views.ActualizacionSedesListApi.as_view()),
    path('db/actualizar_docentes/', rest_views.ActualizacionDocentesListApi.as_view()),

    path('diplomados/', rest_views.DiplomadosListApi.as_view()),
    path('diplomados/<uuid:pk>/niveles/', rest_views.NivelesListApi.as_view()),
    path('diplomados/<uuid:pk>/niveles/<uuid:pk_nivel>/sesiones/', rest_views.SesionesListApi.as_view()),
    path('diplomados/<uuid:pk>/niveles/<uuid:pk_nivel>/sesiones/<uuid:pk_sesion>/actividades/', rest_views.ActividadesListApi.as_view()),
]