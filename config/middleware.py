from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):

        exclude_paths = [
            '/registro/','/registro/completo/','/privacidad/','/verificar/','/verificar','/rest/v1.0/usuarios/recovery/',
            '/perfil/','/logout/','/rest/v1.0/recursos_humanos/certificaciones/cedula/',
            '/rest/v1.0/usuarios/perfil/educacion_superior/','/rest/v1.0/usuarios/municipios/autocomplete/',
            '/rest/v1.0/usuarios/avatar/','/rest/v1.0/usuarios/perfil/experiencia/', '/rest/v1.0/fest_2019/proyectos_api/'
        ]

        if not request.user.is_authenticated:

            if not request.path == settings.LOGIN_URL and not request.path.split('/')[1] == 'oauth' and not request.path.split('/')[1] == 'certificaciones' and not request.path.split('/')[1] == 'media':
                if request.path not in exclude_paths:

                    path_split = request.path.split('/')

                    if 'rest' in path_split and 'v1.0' in path_split and 'fest_2019' in path_split and 'proyectos_api' in path_split and 'rest' in path_split and 'rest' in path_split:
                        pass
                    elif 'rest' in path_split and 'v1.0' in path_split and 'fest_2019' in path_split and 'georeferenciacion_api' in path_split and 'rest' in path_split and 'rest' in path_split:
                        pass
                    else:
                        return redirect(settings.LOGIN_URL)
        else:

            if request.user.cedula == None:
                if request.path not in exclude_paths:
                    if request.path.split('/')[1] != 'media':
                        return redirect('/perfil/')

            else:
                user = request.user
                user.last_online = timezone.now()
                user.save()
                if request.path == settings.LOGIN_URL:
                    return redirect(settings.INIT_URL)