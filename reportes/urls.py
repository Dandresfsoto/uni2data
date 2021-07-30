from django.urls import path
from reportes import views

urlpatterns = [
    path('', views.ReportesView.as_view()),
]