from django.urls import path
from mis_contratos import views

urlpatterns = [
    path('', views.ContratosListView.as_view()),
    path('soportes/<uuid:pk>/', views.ContratosSoportesListView.as_view()),
    path('soportes/<uuid:pk>/editar/<uuid:pk_soporte_contrato>/', views.ContratosSoportesUpdateView.as_view()),
]