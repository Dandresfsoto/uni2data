"""sican_2018 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from config import views
from django.conf import settings
from django.conf.urls.static import static

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('', views.Index.as_view()),
    path('login/', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),
    path('registro/', views.Registro.as_view()),
    path('registro/completo/', views.RegistroCompleto.as_view()),
    path('privacidad/', views.Privacidad.as_view()),
    path('verificar/', views.Verificar.as_view()),

    path('activar/', views.ActivarCuenta.as_view()),
    path('aplicar/<uuid:pk>/', views.AplicarOferta.as_view()),

    path('oauth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),

    path('perfil/', views.Perfil.as_view()),
    path('notificaciones/', views.Notificaciones.as_view()),
    #path('chat/', views.Chat.as_view()),
    path('password/', views.CambioPassword.as_view()),

    path('usuarios/', include('usuarios.urls')),
    path('recursos_humanos/', include('recursos_humanos.urls')),
    path('certificaciones/', include('recursos_humanos.certificaciones_urls')),

    path('direccion_financiera/', include('direccion_financiera.urls')),
    path('reportes/', include('reportes.urls')),
    path('contratos/', include('mis_contratos.urls')),
    path('ofertas/', include('ofertas.urls')),
    #path('cpe_2018/', include('cpe_2018.urls')),
    path('iraca/', include('fest_2019.urls')),
    path('iraca_2021/', include('fest_2020_.urls')),

    path('rest/v1.0/usuarios/', include('usuarios.rest_urls')),
    path('rest/v1.0/recursos_humanos/', include('recursos_humanos.rest_urls')),
    path('rest/v1.0/direccion_financiera/', include('direccion_financiera.rest_urls')),
    path('rest/v1.0/reportes/', include('reportes.rest_urls')),
    path('rest/v1.0/mis_contratos/', include('mis_contratos.rest_urls')),
    path('rest/v1.0/ofertas/', include('ofertas.rest_urls')),
    path('rest/v1.0/cpe_2018/', include('cpe_2018.rest_urls')),
    path('rest/v1.0/fest_2019/', include('fest_2019.rest_urls')),
    path('rest/v1.0/iraca_2021/', include('fest_2020_.rest_urls')),
    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)