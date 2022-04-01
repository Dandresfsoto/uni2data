from django.urls import path

from inventario import rest_views

urlpatterns = [

    path('productos/', rest_views.ProductosListApi.as_view()),

    path('subir/', rest_views.SubirListApi.as_view()),
    path('subir/productos/<uuid:pk>/', rest_views.SubirProductosListApi.as_view()),

    path('despacho/', rest_views.DespachoListApi.as_view()),
    path('despacho/productos/<uuid:pk>/', rest_views.DespachoProductosListApi.as_view()),

    path('productos/list/', rest_views.ProductosListApiJson.as_view()),
    ]