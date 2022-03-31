from django.urls import path, include
from inventario import views

urlpatterns = [
    path('', views.InventarioOptionsView.as_view()),

    path('productos/', views.ProductosListView.as_view()),
    path('productos/create/', views.ProductosCreateView.as_view()),
    path('productos/edit/<uuid:pk>/', views.ProductosEditView.as_view()),

    path('subir/', views.SubirListView.as_view()),
    path('subir/create/', views.SubirCreateView.as_view()),
    path('subir/edit/<uuid:pk>/', views.SubirEditView.as_view()),
    ]