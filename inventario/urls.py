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

    path('subir/productos/<uuid:pk>/', views.SubirProductosListView.as_view()),
    path('subir/productos/<uuid:pk>/create/', views.SubirProductosCreateView.as_view()),
    path('subir/productos/<uuid:pk>/edit/<uuid:pk_adicion>/', views.SubirProductosEditView.as_view()),
    path('subir/productos/<uuid:pk>/delete/<uuid:pk_adicion>/', views.SubirProductosDeleteView.as_view()),
    path('subir/productos/<uuid:pk>/listo/', views.SubirProductosUploadView.as_view()),

    path('despacho/', views.DespachoListView.as_view()),
    path('despacho/create/', views.DespachoCreateView.as_view()),
    path('despacho/edit/<uuid:pk_despacho>/', views.DespachoEditView.as_view()),

    path('despacho/productos/<uuid:pk>/', views.DespachoProductosListView.as_view()),
    path('despacho/productos/<uuid:pk>/create/', views.DespachoProductosCreateView.as_view()),
    path('despacho/productos/<uuid:pk>/edit/<uuid:pk_sustracion>/', views.DespachoProductosEditView.as_view()),
    path('despacho/productos/<uuid:pk>/delete/<uuid:pk_sustracion>/', views.DespachoProductosDeleteView.as_view()),
    path('despacho/productos/<uuid:pk>/listo/', views.DespachoProductosUploadView.as_view()),
]