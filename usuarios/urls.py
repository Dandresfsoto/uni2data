from django.urls import path
from usuarios import views

urlpatterns = [
    path('', views.UsuariosoptionsView.as_view()),
    path('hv/', views.GestionHvView.as_view()),

    path('cuentas/', views.CuentasListView.as_view()),
    path('cuentas/crear/', views.CuentasCreateView.as_view()),
    path('cuentas/editar/<uuid:pk>/', views.CuentasUpdateView.as_view()),

    path('permisos/', views.PermisosListView.as_view()),
    path('permisos/crear/', views.PermisosCreateView.as_view()),
    path('permisos/editar/<int:pk>/', views.PermisosUpdateView.as_view()),

    path('roles/', views.RolesListView.as_view()),
    path('roles/crear/', views.RolesCreateView.as_view()),
    path('roles/editar/<int:pk>/', views.RolesUpdateView.as_view()),

    path('codigos/', views.CodigosListView.as_view()),
    path('codigos/crear/', views.CodigosCreateView.as_view()),
    path('codigos/editar/<uuid:pk>/', views.CodigosUpdateView.as_view()),

    path('codigos/<uuid:pk>/', views.CodigosShowView.as_view()),
]