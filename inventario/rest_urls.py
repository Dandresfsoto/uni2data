from django.urls import path

from inventario import rest_views

urlpatterns = [

    path('productos/', rest_views.ProductosListApi.as_view()),

    path('subir/', rest_views.SubirListApi.as_view()),

    ]