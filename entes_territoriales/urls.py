from django.urls import path
from entes_territoriales import views

urlpatterns = [
    path('', views.EntesTerritorialesOptionsView.as_view()),

    path('reuniones/', views.ReunionesListView.as_view()),
    path('reuniones/reporte/', views.ReporteReunionesListView.as_view()),

    path('reuniones/crear/', views.ReunionesCreateView.as_view()),

    path('reuniones/<uuid:pk>/contactos/', views.ReunionesContactosListView.as_view()),
    path('reuniones/<uuid:pk>/contactos/nuevo/', views.ReunionesContactosCreateView.as_view()),
    path('reuniones/<uuid:pk>/contactos/<uuid:pk_contacto>/editar/', views.ReunionesContactosUpdateView.as_view()),
    path('reuniones/<uuid:pk>/contactos/<uuid:pk_contacto>/soportes/', views.ReunionesContactosSoportesListView.as_view()),
    path('reuniones/<uuid:pk>/contactos/<uuid:pk_contacto>/soportes/nuevo/', views.ReunionesContactosSoportesCreateView.as_view()),
    path('reuniones/<uuid:pk>/contactos/<uuid:pk_contacto>/soportes/<uuid:pk_soporte>/editar/', views.ReunionesContactosSoportesUpdateView.as_view()),

    path('reuniones/<uuid:pk>/hitos/', views.ReunionesHitosListView.as_view()),
    path('reuniones/<uuid:pk>/hitos/<uuid:pk_hito>/editar/', views.ReunionesHitosUpdateView.as_view()),
    path('reuniones/<uuid:pk>/hitos/<uuid:pk_hito>/ver/', views.ReunionesHitosVerView.as_view()),
    path('reuniones/<uuid:pk>/hitos/<uuid:pk_hito>/estado/', views.ReunionesHitosEstadoUpdateView.as_view()),

    path('reuniones/<uuid:pk>/hitos/crear/', views.ReunionesHitosCreateView.as_view()),
    path('reuniones/<uuid:pk>/hitos/gestion/', views.ReunionesHitosGestionListView.as_view()),
]