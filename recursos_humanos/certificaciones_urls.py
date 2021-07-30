from django.urls import path
from recursos_humanos import views

urlpatterns = [
    path('', views.CertificacionesSearchView.as_view()),
    path('<uuid:pk>/', views.CertificacionesPkView.as_view()),
]