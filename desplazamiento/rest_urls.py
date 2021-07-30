from django.urls import path
from desplazamiento import rest_views

urlpatterns = [
    path('', rest_views.SolicitudesDesplazamientoListApi.as_view()),
    path('desplazamientos/<uuid:pk>/', rest_views.DesplazamientosListApi.as_view()),
]