from django.urls import path
from reportes import rest_views

urlpatterns = [
    path('', rest_views.ReportesListApi.as_view()),
]