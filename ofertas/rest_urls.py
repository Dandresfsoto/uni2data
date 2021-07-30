from django.urls import path
from ofertas import rest_views

urlpatterns = [
    path('', rest_views.OfertasListApi.as_view()),
    path('ver/<uuid:pk>/', rest_views.OfertasAplicacionesListApi.as_view()),
    path('resumen/<uuid:pk>/', rest_views.ResumenAplicacionOferta.as_view()),
]