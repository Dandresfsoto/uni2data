from django.urls import path
from ofertas import views

urlpatterns = [
    path('', views.OfertasListView.as_view()),
    path('crear/', views.OfertasCreateView.as_view()),
    path('editar/<uuid:pk>/', views.OfertasUpdateView.as_view()),
    path('aplicar/', views.OfertasPublicListView.as_view()),
    path('aplicar/<uuid:pk>/', views.OfertasAplicarCreateView.as_view()),
    path('ver/<uuid:pk>/', views.OfertaAplicacionesListView.as_view()),
    path('ver/<uuid:pk>/reportes/listado/', views.ReporteOfertaAplicacionesListView.as_view()),
    path('ver/<uuid:pk>/cualificar/<uuid:pk_aplicacion>/', views.CualificarOfertaView.as_view()),
]