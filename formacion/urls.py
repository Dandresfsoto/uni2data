from django.urls import path
from formacion import views

urlpatterns = [
    path('', views.FormacionOptionsView.as_view()),

    path('bd/', views.RegionesSedesListView.as_view()),
    path('bd/<uuid:pk>/departamentos/', views.DepartamentosSedesListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/', views.MunicipiosListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/', views.SedesListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/crear/', views.SedesCreateView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/editar/<uuid:pk_sede>/', views.SedesUpdateView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/<uuid:pk_sede>/formados/', views.FormadosListView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/<uuid:pk_sede>/formados/crear/', views.FormadosCreateView.as_view()),
    path('bd/<uuid:pk>/departamentos/<uuid:pk_departamento>/municipios/<uuid:pk_municipio>/sedes/<uuid:pk_sede>/formados/editar/<uuid:pk_docente>/',views.FormadosUpdateView.as_view()),
    path('bd/actualizar/sedes/', views.ActualizacionDbListView.as_view()),
    path('bd/actualizar/sedes/nuevo/', views.CreateActualizacionDbView.as_view()),
    path('bd/actualizar/docentes/', views.ActualizacionDbDocentesListView.as_view()),
    path('bd/actualizar/docentes/nuevo/', views.CreateActualizacionDbDocentesView.as_view()),




    path('diplomados/', views.DiplomadosListView.as_view()),
    path('diplomados/<uuid:pk>/niveles/', views.NivelesListView.as_view()),
    path('diplomados/<uuid:pk>/niveles/<uuid:pk_nivel>/sesiones/', views.SesionesListView.as_view()),
    path('diplomados/<uuid:pk>/niveles/<uuid:pk_nivel>/sesiones/<uuid:pk_sesion>/actividades/', views.ActividadesListView.as_view()),
]