from django.urls import path
from mis_contratos import rest_views

urlpatterns = [
    path('', rest_views.ContratosListApi.as_view()),
    path('soportes/<uuid:pk>/', rest_views.SoportesContratoListApi.as_view()),
]