from django.urls import path
from usuarios import rest_views

urlpatterns = [
    path('notificaciones/', rest_views.NotificationsApi.as_view()),
    path('cuentas/', rest_views.CuentasListApi.as_view()),
    path('permisos/', rest_views.PermisosListApi.as_view()),
    path('roles/', rest_views.RolesListApi.as_view()),
    path('recovery/', rest_views.RecoveryApi.as_view()),
    path('paquetes/', rest_views.PaquetesListApi.as_view()),
    path('paquetes/<uuid:pk>/', rest_views.PaquetesCodigosListApi.as_view()),
    path('municipios/autocomplete/',rest_views.MunicipiosAutocomplete.as_view()),
    path('perfil/educacion_superior/',rest_views.EducacionSuperiorAPI.as_view()),
    path('perfil/experiencia/',rest_views.ExperienciaAPI.as_view()),
    path('avatar/',rest_views.AvatarAPI.as_view()),
    path('hv/',rest_views.HvAPI.as_view()),
    path('cargar/consejos/', rest_views.cargar_consejos),
    path('cargar/comunidades/', rest_views.cargar_comunidades),
]