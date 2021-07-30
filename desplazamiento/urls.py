from django.urls import path
from desplazamiento import views

urlpatterns = [
    path('', views.SolicitudesDesplazamientoView.as_view()),
    path('crear/', views.SolicitudesDesplazamientoCreateView.as_view()),
    path('editar/<uuid:pk>/', views.SolicitudesDesplazamientoUpdateView.as_view()),

    path('desplazamientos/<uuid:pk>/', views.ListaDesplazamientosView.as_view()),
    path('desplazamientos/<uuid:pk>/crear/', views.DesplazamientosCreateView.as_view()),
    path('desplazamientos/<uuid:pk>/editar/<uuid:pk_desplazamiento>/', views.DesplazamientosUpdateView.as_view()),
    path('desplazamientos/<uuid:pk>/eliminar/<uuid:pk_desplazamiento>/', views.DesplazamientosDeleteView.as_view()),
]