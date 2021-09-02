from django.urls import path, include
from iraca import views

urlpatterns = [
    path('', views.IracaOptionsView.as_view()),


    path('certificate/', views.CerticateOptionsView.as_view()),
    path('certificate/<uuid:pk>/', views.CerticateListView.as_view()),
    path('certificate/<uuid:pk>/create/', views.CerticateCreateView.as_view()),

]