#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django_datatables_view.base_datatable_view import BaseDatatableView
from fest_2019 import models
from django.db.models import Q
from dal import autocomplete
from recursos_humanos import models as rh_models
from fest_2019 import utils
from django.utils import timezone
from usuarios.models import Departamentos, Municipios, Corregimientos, Veredas
from django.shortcuts import render
from uuid import UUID
from django.db.models import Q
from rest_framework import mixins, generics, status
from rest_framework.permissions import AllowAny
from.serializers import ProyectosApiSerializer, GeoreferenciacionApiSerializer


class ProyectosApiView(mixins.CreateModelMixin,
                       generics.GenericAPIView):

    serializer_class = ProyectosApiSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'user': self.request.user}


    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)



class ProyectosApiListView(mixins.ListModelMixin,
                           generics.GenericAPIView):

    serializer_class = ProyectosApiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return models.ProyectosApi.objects.filter(json__documento = str(self.kwargs['cedula']))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)



class ProyectosApiRetrieveView(mixins.RetrieveModelMixin,
                               generics.GenericAPIView):

    serializer_class = ProyectosApiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return models.ProyectosApi.objects.filter(json__documento = str(self.kwargs['cedula']))

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)




class GeoreferenciacionApiView(mixins.CreateModelMixin,
                               generics.GenericAPIView):

    serializer_class = GeoreferenciacionApiSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)




class GeoreferenciacionApiListView(mixins.ListModelMixin,
                                   generics.GenericAPIView):

    serializer_class = GeoreferenciacionApiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return models.GeoreferenciacionApi.objects.filter(json__documento = str(self.kwargs['cedula']))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)



class GeoreferenciacionApiRetrieveView(mixins.RetrieveModelMixin,
                                       generics.GenericAPIView):

    serializer_class = GeoreferenciacionApiSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return models.GeoreferenciacionApi.objects.filter(json__documento = str(self.kwargs['cedula']))

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)





class MiGeoreferenciacionListApi(BaseDatatableView):
    model = models.GeoreferenciacionApi
    columns = ['id','id','id','creation']
    order_columns = ['id','id','id','creation']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.migeoreferenciacion.ver",
            ]
        }

        return self.model.objects.filter(json__documento = str(self.request.user.cedula))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(json__data__document__icontains=search) | Q(json__data__name__icontains=search) | \
                Q(json__data__lastName__icontains=search) | Q(json__data__code__icontains=search)
            qs = qs.filter(q)
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                'Proyecto' if 'type' in item.json['data'].keys() else 'Hogar',
                item.json['data']['code'] if 'type' in item.json['data'].keys() else f'{item.json["data"]["name"]} - {item.json["data"]["document"]}',
                timezone.localtime(item.creation).strftime('%d de %B del %Y a las %I:%M:%S %p'),
                item.json['data']['position']['coords']['latitude'],
                item.json['data']['position']['coords']['longitude'],
                f"{int(item.json['data']['position']['coords']['altitude'])}",
                f"{int(item.json['data']['position']['coords']['accuracy'])} metros",
                f"{item.json['data']['guard']}" if 'guard' in item.json['data'].keys() else "",
                f"{item.json['data']['community']}" if 'community' in item.json['data'].keys() else "",
                '<i class="material-icons" style="color:#00a833">check_circle</i>' if not item.json['data']['position']['mocked'] else '<i class="material-icons" style="color:#f00">cancel</i>',
                f"<div class='center-align'><a target='_blank' href='https://www.google.com/maps/@{item.json['data']['position']['coords']['latitude']},{item.json['data']['position']['coords']['longitude']}' class='tooltipped edit-table' data-position='top' data-delay='50' data-tooltip='Ver en el mapa'><i class='material-icons'>map</i></a></div>"
            ])
        return data



class GeoreferenciacionListApi(BaseDatatableView):
    model = models.GeoreferenciacionApi
    columns = ['id','id','id','creation']
    order_columns = ['id','id','id','creation']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.georeferenciacion.ver",
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(json__data__document__icontains=search) | Q(json__data__name__icontains=search) | \
                Q(json__data__lastName__icontains=search) | Q(json__data__code__icontains=search)
            qs = qs.filter(q)
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                'Proyecto' if 'type' in item.json['data'].keys() else 'Hogar',
                item.json['data']['code'] if item.json['data']['type'] == 'project' else f'{item.json["data"]["name"]} - {item.json["data"]["document"]}',
                timezone.localtime(item.creation).strftime('%d de %B del %Y a las %I:%M:%S %p'),
                item.json['data']['position']['coords']['latitude'],
                item.json['data']['position']['coords']['longitude'],
                f"{int(item.json['data']['position']['coords']['altitude'])}",
                f"{int(item.json['data']['position']['coords']['accuracy'])} metros",
                f"{item.json['data']['guard']}" if 'guard' in item.json['data'].keys() else "",
                f"{item.json['data']['community']}" if 'community' in item.json['data'].keys() else "",
                '<i class="material-icons" style="color:#00a833">check_circle</i>' if not item.json['data']['position']['mocked'] else '<i class="material-icons" style="color:#f00">cancel</i>',
                f"<div class='center-align'><a target='_blank' href='https://www.google.com/maps/@{item.json['data']['position']['coords']['latitude']},{item.json['data']['position']['coords']['longitude']}' class='tooltipped edit-table' data-position='top' data-delay='50' data-tooltip='Ver en el mapa'><i class='material-icons'>map</i></a></div>",
                item.json['nombre'],
                item.json['documento'],
            ])
        return data




class MisProyectosListApi(BaseDatatableView):
    model = models.ProyectosApi
    columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']
    order_columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }

        if self.request.user.id in models.PermisosMisProyectos.objects.all().values_list('user__id', flat=True):
            return self.model.objects.all()

        return self.model.objects.filter(json__documento = str(self.request.user.cedula))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            estados_permitidos = ['Cargado', 'Rechazo profesional local', 'Rechazo equipo monitoreo', 'Rechazo equipo especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar proyecto {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,'')

            return ret

        elif column == 'objetivo_general':
            ret = ''

            estados_permitidos = ['Cargado','Rechazo profesional local','Rechazo equipo monitoreo','Rechazo equipo especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="flujo/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar flujo de caja {1}">' \
                                '<i class="material-icons">monetization_on</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">monetization_on</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'convenio':
            ret = ''

            estados_permitidos = ['Cargado','Rechazo profesional local','Rechazo equipo monitoreo','Rechazo equipo especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="identificacion/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar identificacion de proyectos {1}">' \
                                '<i class="material-icons">chrome_reader_mode</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">chrome_reader_mode</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'problematica_1_1':

            ret = '<div class="center-align">' \
                       '<a href="observaciones/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver las observaciones del proyecto {1}">' \
                            '<i class="material-icons">chat</i>' \
                       '</a>' \
                   '</div>'.format(row.id,'')

            return ret



        elif column == 'estado':

            estados_permitidos = ['Cargado','Rechazo profesional local','Rechazo equipo monitoreo','Rechazo equipo especialistas']

            if row.estado in estados_permitidos:

                ret = '<div class="center-align">' \
                           '<a href="estado/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar estado del proyecto">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.estado)

            else:

                ret = '<div class="center-align">' \
                            '<b>{1}</b>' \
                       '</div>'.format(row.id,row.estado)

            return ret


        elif column == 'municipio':
            municipio = ''

            if row.municipio != None:
                municipio = f'{row.municipio.departamento.nombre}, {row.municipio.nombre}'

            return municipio

        elif column == 'creation':

            fecha = timezone.localtime(row.creation).strftime('%d de %B del %Y a las %I:%M:%S %p')

            if row.actualizar_app:

                ret = '<span>{0}</span><a href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Este proyecto se puede actualizar desde la app movil">' \
                            '<i class="material-icons">system_update</i>' \
                        '</a>'.format(fecha)
            else:
                ret = fecha

            return ret


        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'numero_hogares':
            ret = '<div class="center-align">' \
                      '<a href="hogares/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<b>{2}</b>' \
                      '</a>' \
                  '</div>'.format(row.id, 'Ver hogares del proyecto',row.numero_hogares)
            return ret

        else:
            return super(MisProyectosListApi, self).render_column(row, column)




"""
class ProyectosLocalListApi(BaseDatatableView):
    model = models.ProyectosApi
    columns = ['id','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']
    order_columns = ['id','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        departamentos_ids = models.PermisosCuentasDepartamentos.objects.filter(users = self.request.user).values_list('departamento__id',flat=True).distinct()
        return self.model.objects.filter(municipio__departamento__id__in = departamentos_ids)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            estados_permitidos = ['Enviado a revisión por profesional local']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="verificar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Verificar proyecto {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'problematica_1_1':

            ret = '<div class="center-align">' \
                       '<a href="observaciones/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver las observaciones del proyecto {1}">' \
                            '<i class="material-icons">chat</i>' \
                       '</a>' \
                   '</div>'.format(row.id,'')

            return ret


        elif column == 'municipio':
            municipio = ''

            if row.municipio != None:
                municipio = f'{row.municipio.departamento.nombre}, {row.municipio.nombre}'

            return municipio


        elif column == 'creation':

            fecha = timezone.localtime(row.creation).strftime('%d de %B del %Y a las %I:%M:%S %p')

            if row.actualizar_app:
                ret = '<span>{0}</span><a href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Este proyecto se puede actualizar desde la app movil">' \
                      '<i class="material-icons">system_update</i>' \
                      '</a>'.format(fecha)

            else:

                ret = fecha

            return ret


        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'numero_hogares':
            ret = '<div class="center-align">' \
                      '<a href="hogares/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<b>{2}</b>' \
                      '</a>' \
                  '</div>'.format(row.id, 'Ver hogares del proyecto',row.numero_hogares)
            return ret

        else:
            return super(ProyectosLocalListApi, self).render_column(row, column)
"""


class ProyectosLocalListApi(BaseDatatableView):
    model = models.ProyectosApi
    columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']
    order_columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        departamentos_ids = models.PermisosCuentasDepartamentos.objects.filter(users = self.request.user).values_list('departamento__id',flat=True).distinct()
        return self.model.objects.filter(municipio__departamento__id__in = departamentos_ids)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            estados_permitidos = ['Enviado a revisión por profesional local']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar proyecto {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,'')

            return ret

        elif column == 'objetivo_general':
            ret = ''

            estados_permitidos = ['Enviado a revisión por profesional local']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="flujo/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar flujo de caja {1}">' \
                                '<i class="material-icons">monetization_on</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">monetization_on</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'convenio':
            ret = ''

            estados_permitidos = ['Enviado a revisión por profesional local']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="identificacion/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar identificacion de proyectos {1}">' \
                                '<i class="material-icons">chrome_reader_mode</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">chrome_reader_mode</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'problematica_1_1':

            ret = '<div class="center-align">' \
                       '<a href="observaciones/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver las observaciones del proyecto {1}">' \
                            '<i class="material-icons">chat</i>' \
                       '</a>' \
                   '</div>'.format(row.id,'')

            return ret


        elif column == 'estado':

            estados_permitidos = ['Enviado a revisión por profesional local']

            if row.estado in estados_permitidos:

                ret = '<div class="center-align">' \
                           '<a href="estado/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar estado del proyecto">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.estado)

            else:

                ret = '<div class="center-align">' \
                            '<b>{1}</b>' \
                       '</div>'.format(row.id,row.estado)

            return ret


        elif column == 'municipio':
            municipio = ''

            if row.municipio != None:
                municipio = f'{row.municipio.departamento.nombre}, {row.municipio.nombre}'

            return municipio

        elif column == 'creation':

            fecha = timezone.localtime(row.creation).strftime('%d de %B del %Y a las %I:%M:%S %p')

            if row.actualizar_app:

                ret = '<span>{0}</span><a href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Este proyecto se puede actualizar desde la app movil">' \
                            '<i class="material-icons">system_update</i>' \
                        '</a>'.format(fecha)
            else:
                ret = fecha

            return ret


        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'numero_hogares':
            ret = '<div class="center-align">' \
                      '<a href="hogares/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<b>{2}</b>' \
                      '</a>' \
                  '</div>'.format(row.id, 'Ver hogares del proyecto',row.numero_hogares)
            return ret

        else:
            return super(ProyectosLocalListApi, self).render_column(row, column)



class ProyectosMonitoreoListApi(BaseDatatableView):
    model = models.ProyectosApi
    columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']
    order_columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            estados_permitidos = ['Vo Bo profesional local', 'Enviado a revisión equipo monitoreo']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar proyecto {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,'')

            return ret

        elif column == 'objetivo_general':
            ret = ''

            estados_permitidos = ['Vo Bo profesional local','Enviado a revisión equipo monitoreo']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="flujo/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar flujo de caja {1}">' \
                                '<i class="material-icons">monetization_on</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">monetization_on</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'convenio':
            ret = ''

            estados_permitidos = ['Vo Bo profesional local','Enviado a revisión equipo monitoreo']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="identificacion/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar identificacion de proyectos {1}">' \
                                '<i class="material-icons">chrome_reader_mode</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">chrome_reader_mode</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'problematica_1_1':

            ret = '<div class="center-align">' \
                       '<a href="observaciones/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver las observaciones del proyecto {1}">' \
                            '<i class="material-icons">chat</i>' \
                       '</a>' \
                   '</div>'.format(row.id,'')

            return ret


        elif column == 'estado':

            estados_permitidos = ['Vo Bo profesional local','Enviado a revisión equipo monitoreo']

            if row.estado in estados_permitidos:

                ret = '<div class="center-align">' \
                           '<a href="estado/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar estado del proyecto">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.estado)

            else:

                ret = '<div class="center-align">' \
                            '<b>{1}</b>' \
                       '</div>'.format(row.id,row.estado)

            return ret


        elif column == 'municipio':
            municipio = ''

            if row.municipio != None:
                municipio = f'{row.municipio.departamento.nombre}, {row.municipio.nombre}'

            return municipio

        elif column == 'creation':

            fecha = timezone.localtime(row.creation).strftime('%d de %B del %Y a las %I:%M:%S %p')

            if row.actualizar_app:

                ret = '<span>{0}</span><a href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Este proyecto se puede actualizar desde la app movil">' \
                            '<i class="material-icons">system_update</i>' \
                        '</a>'.format(fecha)
            else:
                ret = fecha

            return ret


        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'numero_hogares':
            ret = '<div class="center-align">' \
                      '<a href="hogares/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<b>{2}</b>' \
                      '</a>' \
                  '</div>'.format(row.id, 'Ver hogares del proyecto',row.numero_hogares)
            return ret

        else:
            return super(ProyectosMonitoreoListApi, self).render_column(row, column)



class ProyectosEspecialistasListApi(BaseDatatableView):
    model = models.ProyectosApi
    columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']
    order_columns = ['id','objetivo_general','convenio','creation','tipo_proyecto','codigo_proyecto','nombre_proyecto','municipio','numero_hogares','valor', 'file', 'estado', 'problematica_1_1']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            estados_permitidos = ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar proyecto {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,'')

            return ret

        elif column == 'objetivo_general':
            ret = ''

            estados_permitidos = ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="flujo/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar flujo de caja {1}">' \
                                '<i class="material-icons">monetization_on</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">monetization_on</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'convenio':
            ret = ''

            estados_permitidos = ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']

            if self.request.user.has_perms(self.permissions.get('editar')) and row.estado in estados_permitidos:
                ret = '<div class="center-align">' \
                           '<a href="identificacion/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar identificacion de proyectos {1}">' \
                                '<i class="material-icons">chrome_reader_mode</i>' \
                           '</a>' \
                       '</div>'.format(row.id,'')

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">chrome_reader_mode</i>' \
                       '</div>'.format(row.id,'')

            return ret


        elif column == 'problematica_1_1':

            ret = '<div class="center-align">' \
                       '<a href="observaciones/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver las observaciones del proyecto {1}">' \
                            '<i class="material-icons">chat</i>' \
                       '</a>' \
                   '</div>'.format(row.id,'')

            return ret


        elif column == 'estado':

            estados_permitidos = ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']

            if row.estado in estados_permitidos:

                ret = '<div class="center-align">' \
                           '<a href="estado/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar estado del proyecto">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.estado)

            else:

                ret = '<div class="center-align">' \
                            '<b>{1}</b>' \
                       '</div>'.format(row.id,row.estado)

            return ret


        elif column == 'municipio':
            municipio = ''

            if row.municipio != None:
                municipio = f'{row.municipio.departamento.nombre}, {row.municipio.nombre}'

            return municipio

        elif column == 'creation':

            fecha = timezone.localtime(row.creation).strftime('%d de %B del %Y a las %I:%M:%S %p')

            if row.actualizar_app:

                ret = '<span>{0}</span><a href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Este proyecto se puede actualizar desde la app movil">' \
                            '<i class="material-icons">system_update</i>' \
                        '</a>'.format(fecha)
            else:
                ret = fecha

            return ret


        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'numero_hogares':
            ret = '<div class="center-align">' \
                      '<a href="hogares/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<b>{2}</b>' \
                      '</a>' \
                  '</div>'.format(row.id, 'Ver hogares del proyecto',row.numero_hogares)
            return ret

        else:
            return super(ProyectosEspecialistasListApi, self).render_column(row, column)



class HogaresListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','rutas']
    order_columns = ['id','documento','primer_nombre','municipio','rutas']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.db.ver"
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.db.ver",
                "usuarios.fest_2019.db.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)




        elif column == 'rutas':
            return row.get_rutas()



        else:
            return super(HogaresListApi, self).render_column(row, column)



#------------------------------------- ENTREGABLES -------------------------------------


class EntregablesListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','nombre','consecutivo','momentos']
    order_columns = ['id','nombre','consecutivo','momentos']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.entregables.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/momentos/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver momentos del componente {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'momentos':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_numero_momentos())

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)

        else:
            return super(EntregablesListApi, self).render_column(row, column)

class MomentosListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id','nombre','consecutivo','instrumentos','tipo']
    order_columns = ['id','nombre','consecutivo','instrumentos','tipo']

    def get_initial_queryset(self):
        self.componente = models.Componentes.objects.get(pk = self.kwargs['pk_componente'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.entregables.ver"
            ]
        }
        return self.model.objects.filter(componente = self.componente)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/instrumentos/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes de la visita: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'instrumentos':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_numero_instrumentos())

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutivo())

        else:
            return super(MomentosListApi, self).render_column(row, column)

class InstrumentosListApi(BaseDatatableView):
    model = models.Instrumentos
    columns = ['nombre','consecutivo','modelo', 'id']
    order_columns = ['nombre','consecutivo','modelo', 'id']

    def get_initial_queryset(self):
        self.componente = models.Componentes.objects.get(pk = self.kwargs['pk_componente'])
        self.momento = models.Momentos.objects.get(pk=self.kwargs['pk_momento'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.entregables.ver"
            ]
        }
        return self.model.objects.filter(momento = self.momento)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="informe/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar informe: {1}">' \
                      '<i class="material-icons">email</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">email</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutivo())


        else:
            return super(InstrumentosListApi, self).render_column(row, column)



#------------------------------------- RUTAS -------------------------------------

class RutasListApi(BaseDatatableView):
    model = models.Rutas
    columns = ['id','creation','nombre','contrato','componente','valor','novedades','progreso','hogares_inscritos','usuario_creacion']
    order_columns = ['id','creation','nombre','contrato','componente','valor','novedades','progreso','hogares_inscritos','usuario_creacion']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.editar"
            ],
            "ver_hogares": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver"
            ]
        }
        if self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            try:
                permiso = models.PermisosCuentasRutas.objects.get(user = self.request.user)
            except:
                return self.model.objects.none()
            else:
                ids_ver = permiso.rutas_ver.values_list('id',flat=True)
                return self.model.objects.filter(id__in = ids_ver)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar ruta {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'contrato':
            return row.contrato.contratista.get_full_name_cedula()

        elif column == 'componente':
            return row.componente.nombre

        elif column == 'novedades':
            if row.novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(row.novedades)
            else:
                return ''

        elif column == 'valor':

            tooltip = '<p>Ruta: {0}</p>' \
                      '<p>Transporte ruta: {1}</p>' \
                      '<p>Transporte ruta: {2}</p>'.format(
                utils.col2str(row.valor - row.valor_transporte -row.valor_otros),
                utils.col2str(row.valor_transporte),
                utils.col2str(row.valor_otros)
            )

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(utils.col2str(row.valor),tooltip)

        elif column == 'progreso':

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-delay="50" ' \
                   'data-tooltip="Progreso general de la ruta">' \
                   '<b>{0}%</b>' \
                   '</a>' \
                   '</div>'.format(row.progreso)

        elif column == 'hogares_inscritos':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver_hogares')):
                ret = '<div class="center-align">' \
                           '<a href="hogares/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="{1} hogares inscritos">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.hogares_inscritos)

            else:
                ret = '<div class="center-align">' \
                           '<b>{1}</b>' \
                       '</div>'.format(row.id,row.hogares_inscritos)

            return ret

        elif column == 'usuario_creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="cuentas_cobro/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro de la ruta {1}">' \
                                '<i class="material-icons">account_balance_wallet</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">account_balance_wallet</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        else:
            return super(RutasListApi, self).render_column(row, column)

class HogaresRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio']
    order_columns = ['id','documento','primer_nombre','municipio']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver"
            ]
        }

        return self.model.objects.filter(rutas = self.ruta)



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver información del hogar">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)



        else:
            return super(HogaresRutasListApi, self).render_column(row, column)

class ContratosAutocomplete(autocomplete.Select2QuerySetView):

    def get_results(self, context):

        data = []

        for result in context['object_list']:


            data.append({
                'id': self.get_result_value(result),
                'text': result.get_autocomplete_text(),
            })


        return data

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return rh_models.Contratos.objects.none()

        qs = rh_models.Contratos.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(contratista__nombres__icontains = self.q) | \
                Q(contratista__apellidos__icontains = self.q) | Q(contratista__cedula__icontains = self.q)
            qs = qs.filter(q)

        return qs

class HogaresActividadesListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id', 'consecutivo', 'nombre', 'tipo' ,'valor_maximo', 'novedades', 'progreso']
    order_columns = ['id', 'consecutivo', 'nombre', 'tipo','valor_maximo', 'novedades', 'progreso']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if self.request.user.is_superuser:
            return self.model.objects.filter(componente = self.ruta.componente)
        else:
            ids_ver = self.permiso.rutas_ver.all()
            if self.ruta in ids_ver:
                return self.model.objects.filter(componente=self.ruta.componente)
            else:
                return self.model.objects.none()


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(consecutivo__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''


            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)


        elif column == 'tipo':
            return '<div class="center-align">{0}</div>'.format(row.get_cantidad_momento(self.ruta))



        elif column == 'valor_maximo':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_maximo_momento(self.ruta))

        elif column == 'novedades':
            novedades = row.get_novedades_mis_rutas_actividades(self.ruta)

            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''

        elif column == 'progreso':

            progreso_tuple = row.get_progreso_momento(self.ruta)

            progreso = '{:20,.2f}%'.format(progreso_tuple[0])

            tooltip = '<p>Reportado: {0}</p>' \
                      '<p>Pagado: {1}</p>'.format(
                '$ {:20,.2f}'.format(progreso_tuple[2]),
                '$ {:20,.2f}'.format(progreso_tuple[3])
            )

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso,tooltip)





        else:
            return super(HogaresActividadesListApi, self).render_column(row, column)




class HogaresActividadesObjetosListApi(BaseDatatableView):
    model = models.CuposRutaObject
    columns = ['hogar', 'corte', 'estado', 'valor', 'translado']
    order_columns = ['hogar', 'corte', 'estado', 'valor', 'translado']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        return self.model.objects.filter(ruta = self.ruta, momento = self.momento)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(hogar__documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            return ''

        elif column == 'hogar':
            if row.hogar != None:
                return row.hogar.documento
            else:
                return ''

        elif column == 'corte':
            if row.corte != None:
                return str(row.corte)
            else:
                return ''

        elif column == 'valor':
            return str(row.valor)

        elif column == 'translado':
            if row.translado:
                return 'Si'
            else:
                return 'No'


        elif column == 'estado':

            """
            if self.request.user.is_superuser and row.estado == 'asignado' and not row.translado and row.momento.nombre == 'Visita 1':
                ret = '<div class="center-align">' \
                           '<a href="cero/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Reportar en cero">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.estado)
            """

            ret = '<div class="center-align">' \
                       '<b>{0}</b>' \
                   '</div>'.format(row.estado)


            return ret


        else:
            return super(HogaresActividadesObjetosListApi, self).render_column(row, column)




class ActividadesHogaresRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','id_archivo','id_elegible','telefono']
    order_columns = ['id','documento','primer_nombre','municipio','id_archivo','id_elegible','telefono']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None


        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if self.request.user.is_superuser:
            if self.momento.tipo == 'vinculacion':
                ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in = ids))
            else:
                if self.momento.nombre == 'Visita 1':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in = ids))
                else:
                    if str(self.ruta.componente.consecutivo) == '1':
                        ids = models.CuposRutaObject.objects.filter(ruta = self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                        return self.model.objects.filter(Q(ruta_1=self.ruta) | Q(id__in = ids))
                    elif str(self.ruta.componente.consecutivo) == '2':
                        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id', flat=True).distinct()
                        return self.model.objects.filter(Q(ruta_2=self.ruta) | Q(id__in = ids))
                    elif str(self.ruta.componente.consecutivo) == '3':
                        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id', flat=True).distinct()
                        return self.model.objects.filter(Q(ruta_3=self.ruta) | Q(id__in = ids))
                    elif str(self.ruta.componente.consecutivo) == '4':
                        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id', flat=True).distinct()
                        return self.model.objects.filter(Q(ruta_4=self.ruta) | Q(id__in = ids))
                    else:
                        return self.model.objects.none()
        else:
            ids_ver = self.permiso.rutas_ver.all()
            if self.ruta in ids_ver:
                if self.momento.tipo == 'vinculacion':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in = ids))
                else:
                    if self.momento.nombre == 'Visita 1':
                        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                        return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in = ids))
                    else:
                        if str(self.ruta.componente.consecutivo) == '1':
                            ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                            return self.model.objects.filter(Q(ruta_1=self.ruta) | Q(id__in = ids))
                        elif str(self.ruta.componente.consecutivo) == '2':
                            ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                            return self.model.objects.filter(Q(ruta_2=self.ruta) | Q(id__in = ids))
                        elif str(self.ruta.componente.consecutivo) == '3':
                            ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                            return self.model.objects.filter(Q(ruta_3=self.ruta) | Q(id__in = ids))
                        elif str(self.ruta.componente.consecutivo) == '4':
                            ids = models.CuposRutaObject.objects.filter(ruta=self.ruta,momento=self.momento).values_list('hogar__id',flat=True).distinct()
                            return self.model.objects.filter(Q(ruta_4=self.ruta) | Q(id__in = ids))
                        else:
                            return self.model.objects.none()
            else:
                return self.model.objects.none()


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los instrumentos de la visita">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)


        elif column == 'id_archivo':
            novedades = row.get_novedades_mis_rutas_momento(self.ruta,self.momento)
            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''

        elif column == 'id_elegible':
            return row.get_estado_valor(self.ruta,self.momento)

        elif column == 'telefono':
            return row.get_estado(self.ruta,self.momento)

        else:
            return super(ActividadesHogaresRutasListApi, self).render_column(row, column)

class InstrumentosHogaresRutasListApi(BaseDatatableView):
    model = models.InstrumentosRutaObject
    columns = ['creacion','cupo_object','id','consecutivo', 'nombre', 'estado', 'modelo','ruta','observacion']
    order_columns = ['creacion','cupo_object','id', 'consecutivo', 'nombre', 'estado', 'modelo','ruta','observacion']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if self.request.user.is_superuser:
            return self.model.objects.filter(ruta=self.ruta, momento=self.momento)
        else:
            ids_ver = self.permiso.rutas_ver.all()
            if self.ruta in ids_ver:
                return self.model.objects.filter(ruta=self.ruta, momento=self.momento)
            else:
                return self.model.objects.none()


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(hogares__documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,utils.pretty_datetime(timezone.localtime(row.fecha_actualizacion)))

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="trazabilidad/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">class</i>' \
                      '</a>' \
                      '</div>'.format(row.id, 'Ver la trazabilidad')

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">class</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'consecutivo':
            return row.get_hogares_list()


        elif column == 'cupo_object':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):

                if row.estado in ['cargado', 'rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar el soporte">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id)


                else:

                    ret = '<div class="center-align">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'modelo':

            valor = ''

            if row.cupo_object != None and row.cupo_object != '':
                valor = str(row.cupo_object.valor)

            return valor



        elif column == 'nombre':
            return row.nombre


        elif column == 'estado':
            ret = ''
            if row.estado == 'cargado':
                ret = ''
            return row.estado

        elif column == 'observacion':

            if row.estado in ['cargado']:

                ret = '<div class="center-align">' \
                      '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                      '<i class="material-icons">delete</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:

                ret = '<div class="center-align">' \
                      '<i class="material-icons">delete</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'ruta':
            ret = ''

            if self.request.user.is_superuser:
                if row.estado != 'aprobado':

                    if row.cupo_object != None and row.cupo_object != '':
                        if row.cupo_object.estado not in ['Pagado']:
                            ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                   '<i class="material-icons">{2}</i>' \
                                   '</a>'.format(row.id, 'Aprobar', 'check_box')

                    else:
                        ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Aprobar', 'check_box')

                if row.estado != 'rechazado':
                    if row.cupo_object != None and row.cupo_object != '':

                        if row.cupo_object.estado not in ['Pagado']:
                            ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                   '<i class="material-icons">{2}</i>' \
                                   '</a>'.format(row.id, 'Rechazar', 'highlight_off')

                    else:
                        ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Rechazar', 'highlight_off')


            elif self.permiso != None:

                if self.ruta.id in self.permiso.rutas_aprobar.values_list('id',flat=True):

                    if row.estado != 'aprobado':

                        if row.cupo_object != None and row.cupo_object != '':
                            if row.cupo_object.estado not in ['Pagado']:
                                ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                       '<i class="material-icons">{2}</i>' \
                                       '</a>'.format(row.id, 'Aprobar', 'check_box')

                        else:
                            ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                        '<i class="material-icons">{2}</i>' \
                                   '</a>'.format(row.id,'Aprobar','check_box')

                    if row.estado != 'rechazado':
                        if row.cupo_object != None and row.cupo_object != '':

                            if row.cupo_object.estado not in ['Pagado']:
                                ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                       '<i class="material-icons">{2}</i>' \
                                       '</a>'.format(row.id, 'Rechazar', 'highlight_off')

                        else:
                            ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                        '<i class="material-icons">{2}</i>' \
                                   '</a>'.format(row.id, 'Rechazar', 'highlight_off')
            else:
                pass
            return '<div class="center-align">' + ret + '</div>'

        else:
            return super(InstrumentosHogaresRutasListApi, self).render_column(row, column)


class InstrumentosHogaresRutasTrazabilidadListApi(BaseDatatableView):
    model = models.InstrumentosTrazabilidadRutaObject
    columns = ['creacion','user','observacion']
    order_columns = ['creacion','user','observacion']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=self.request.user)
        except:
            self.permiso = None

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if self.request.user.is_superuser:
            return self.model.objects.filter(instrumento=self.instrumento_object)
        else:
            ids_ver = self.permiso.rutas_ver.all()
            if self.ruta in ids_ver:
                return self.model.objects.filter(instrumento=self.instrumento_object)
            else:
                return self.model.objects.none()



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            return timezone.localtime(row.creacion).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'user':
            return row.user.get_full_name()


        else:
            return super(InstrumentosHogaresRutasTrazabilidadListApi, self).render_column(row, column)

#----------------------------------- MIS RUTAS ------------------------------------

class MisRutasListApi(BaseDatatableView):
    model = models.Rutas
    columns = ['creation', 'nombre', 'contrato', 'componente', 'valor', 'novedades', 'progreso', 'hogares_inscritos', 'valores_actividades']
    order_columns = ['creation', 'nombre', 'contrato', 'componente', 'valor', 'novedades', 'progreso', 'hogares_inscritos', 'valores_actividades']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }
        return self.model.objects.filter(contrato__contratista__usuario_asociado = self.request.user)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__cedula__icontains=search) | \
                Q(contrato__contratista__nombres__icontains=search) | Q(contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'contrato':
            return row.contrato.contratista.get_full_name_cedula()

        elif column == 'componente':
            return row.componente.nombre

        elif column == 'novedades':
            if row.novedades > 0:
                return '<div class="center-align"><span class="new badge" data-badge-caption="">{0}</span></div>'.format(row.novedades)
            else:
                return ''

        elif column == 'valor':

            tooltip = '<p>Ruta: {0}</p>' \
                      '<p>Transporte ruta: {1}</p>' \
                      '<p>Otros valores ruta: {2}</p>'.format(
                utils.col2str(row.valor - row.valor_transporte -row.valor_otros),
                utils.col2str(row.valor_transporte),
                utils.col2str(row.valor_otros),
            )

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(utils.col2str(row.valor),tooltip)

        elif column == 'progreso':

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-delay="50" ' \
                   'data-tooltip="Progreso general de la ruta">' \
                   '<b>{0}%</b>' \
                   '</a>' \
                   '</div>'.format(row.progreso)

        elif column == 'hogares_inscritos':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="hogares/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="{1} hogares asignados">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.hogares_inscritos)

            else:
                ret = '<div class="center-align">' \
                           '<b>{1}</b>' \
                       '</div>'.format(row.id,row.hogares_inscritos)

            return ret

        elif column == 'valores_actividades':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="cuentas_cobro/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro de la ruta {1}">' \
                                '<i class="material-icons">account_balance_wallet</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">account_balance_wallet</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        else:
            return super(MisRutasListApi, self).render_column(row, column)

class HogaresMisRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id', 'documento', 'primer_nombre', 'municipio']
    order_columns = ['id', 'documento', 'primer_nombre', 'municipio']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver"
            ]
        }

        return self.model.objects.filter(rutas = self.ruta)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver información del hogar">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)


        else:
            return super(HogaresMisRutasListApi, self).render_column(row, column)

class HogaresMisActividadesListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo', 'novedades', 'progreso']
    order_columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo', 'novedades', 'progreso']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver"
            ]
        }

        return self.model.objects.filter(componente = self.ruta.componente)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(consecutivo__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''


            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)


        elif column == 'tipo':
            return '<div class="center-align">{0}</div>'.format(row.get_cantidad_momento(self.ruta))



        elif column == 'valor_maximo':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_maximo_momento(self.ruta))

        elif column == 'novedades':
            novedades = row.get_novedades_mis_rutas_actividades(self.ruta)

            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''

        elif column == 'progreso':

            progreso_tuple = row.get_progreso_momento(self.ruta)

            progreso = '{:20,.2f}%'.format(progreso_tuple[0])

            tooltip = '<p>Reportado: {0}</p>' \
                      '<p>Pagado: {1}</p>'.format(
                '$ {:20,.2f}'.format(progreso_tuple[2]),
                '$ {:20,.2f}'.format(progreso_tuple[3])
            )

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso,tooltip)


        else:
            return super(HogaresMisActividadesListApi, self).render_column(row, column)



class MiembrosHogaresMisRutasListApi(BaseDatatableView):
    model = models.MiembroNucleoHogar
    columns = ['id', 'numero_documento', 'primer_nombre', 'parentezco']
    order_columns = ['id', 'numero_documento', 'primer_nombre', 'parentezco']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver"
            ]
        }

        return self.model.objects.filter(hogar=self.hogar)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | Q(numero_documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver informción del integrante">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'primer_nombre':
            return row.get_fullname()


        else:
            return super(MiembrosHogaresMisRutasListApi, self).render_column(row, column)

class MiembrosHogaresRutasListApi(BaseDatatableView):
    model = models.MiembroNucleoHogar
    columns = ['id', 'numero_documento', 'primer_nombre', 'parentezco']
    order_columns = ['id', 'numero_documento', 'primer_nombre', 'parentezco']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver"
            ]
        }

        return self.model.objects.filter(hogar=self.hogar)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | Q(numero_documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver informción del integrante">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'primer_nombre':
            return row.get_fullname()


        else:
            return super(MiembrosHogaresRutasListApi, self).render_column(row, column)

class MisActividadesHogaresRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','id_archivo','id_elegible','telefono']
    order_columns = ['id','documento','primer_nombre','municipio','id_archivo','id_elegible','telefono']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver"
            ]
        }


        if self.momento.tipo == 'vinculacion':
            ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id',flat=True).distinct()
            return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in=ids))
        else:
            if self.momento.nombre == 'Visita 1':
                ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id', flat=True).distinct()
                return self.model.objects.filter(Q(ruta_vinculacion=self.ruta) | Q(id__in=ids))
            else:
                if str(self.ruta.componente.consecutivo) == '1':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id', flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_1=self.ruta) | Q(id__in=ids))
                elif str(self.ruta.componente.consecutivo) == '2':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id', flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_2=self.ruta) | Q(id__in=ids))
                elif str(self.ruta.componente.consecutivo) == '3':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id', flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_3=self.ruta) | Q(id__in=ids))
                elif str(self.ruta.componente.consecutivo) == '4':
                    ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, momento=self.momento).values_list('hogar__id', flat=True).distinct()
                    return self.model.objects.filter(Q(ruta_4=self.ruta) | Q(id__in=ids))
                else:
                    return self.model.objects.none()




    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los instrumentos de la visita">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)

        elif column == 'id_archivo':
            novedades = row.get_novedades_mis_rutas_momento(self.ruta,self.momento)
            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''


        elif column == 'id_elegible':

            return row.get_estado_valor(self.ruta, self.momento)


        elif column == 'telefono':

            return row.get_estado(self.ruta, self.momento)


        else:
            return super(MisActividadesHogaresRutasListApi, self).render_column(row, column)

class MisInstrumentosHogaresRutasListApi(BaseDatatableView):
    model = models.InstrumentosRutaObject
    columns = ['id', 'creacion', 'consecutivo' ,'nombre', 'estado', 'modelo','usuario_creacion', 'hogar']
    order_columns = ['id', 'creacion', 'consecutivo', 'nombre', 'estado', 'modelo', 'usuario_creacion', 'hogar']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver"
            ]
        }

        return self.model.objects.filter(ruta=self.ruta,momento=self.momento)




    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(hogares__documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):

                if row.estado in ['cargado','rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar el soporte">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id)


                else:

                    ret = '<div class="center-align">' \
                               '<i class="material-icons">cloud_upload</i>' \
                           '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,utils.pretty_datetime(timezone.localtime(row.fecha_actualizacion)))

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':
            return row.get_hogares_list()




        elif column == 'modelo':

            valor = ''

            if row.cupo_object != None and row.cupo_object != '':
                valor = str(row.cupo_object.valor)

            return valor



        elif column == 'estado':
            return row.estado

        elif column == 'usuario_creacion':

            if row.estado in ['cargado']:

                ret = '<div class="center-align">' \
                      '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                      '<i class="material-icons">delete</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:

                ret = '<div class="center-align">' \
                      '<i class="material-icons">delete</i>' \
                      '</div>'.format(row.id)

            return ret



        elif column == 'hogar':


            ret = '<div class="center-align">' \
                  '<a href="observaciones/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver observaciones">' \
                  '<i class="material-icons">chat</i>' \
                  '</a>' \
                  '</div>'.format(row.id)

            return ret


        else:
            return super(MisInstrumentosHogaresRutasListApi, self).render_column(row, column)




class MisInstrumentosHogaresRutasObservacionesListApi(BaseDatatableView):
    model = models.ObservacionesInstrumentoRutaObject
    columns = ['creacion', 'usuario_creacion', 'observacion']
    order_columns = ['creacion', 'usuario_creacion', 'observacion']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver"
            ]
        }

        return self.model.objects.filter(instrumento = self.instrumento_object)




    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(usuario_creacion__email__icontains=search) | Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creacion':
            return row.pretty_creation_datetime()


        elif column == 'usuario_creacion':
            return row.usuario_creacion.email


        else:
            return super(MisInstrumentosHogaresRutasObservacionesListApi, self).render_column(row, column)



def cargar_municipios(request):
    departamento_id = request.GET.get('departamento')
    try:
        UUID(departamento_id)
    except:
        municipios = Municipios.objects.none()
    else:
        municipios = Municipios.objects.filter(departamento=departamento_id).order_by('nombre')

    return render(request, 'fest_2019/misrutas/load/municipios_dropdown_list_options.html', {'municipios': municipios})


def cargar_corregimientos(request):
    municipio_id = request.GET.get('municipio')
    try:
        UUID(municipio_id)
    except:
        corregimientos = Corregimientos.objects.none()
    else:
        corregimientos = Corregimientos.objects.filter(municipio=municipio_id).order_by('nombre')

    return render(request, 'fest_2019/misrutas/load/corregimientos_dropdown_list_options.html', {'corregimientos': corregimientos})



def cargar_veredas(request):
    municipio_id = request.GET.get('municipio')
    try:
        UUID(municipio_id)
    except:
        veredas = Veredas.objects.none()
    else:
        veredas = Veredas.objects.filter(municipio=municipio_id).order_by('nombre')

    return render(request, 'fest_2019/misrutas/load/veredas_dropdown_list_options.html', {'veredas': veredas})

#------------------------------------- PERMISOS -------------------------------------

class PermisosListApi(BaseDatatableView):
    model = models.PermisosCuentasRutas
    columns = ['id', 'user', 'rutas_ver']
    order_columns = ['id', 'user', 'rutas_ver']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver"
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.editar"
            ]
        }

        return self.model.objects.all()




    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(user__email__icontains=search) | Q(user__first_name__icontains=search) | \
                Q(user__last_name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Actualizar permisos de la cuenta">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'user':
            return row.user.email

        elif column == 'rutas_ver':
            return row.user.get_full_name_string()

        else:
            return super(PermisosListApi, self).render_column(row, column)


class PermisosProyectosListApi(BaseDatatableView):
    model = models.PermisosCuentasDepartamentos
    columns = ['id', 'departamento', 'users']
    order_columns = ['id', 'departamento', 'users']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver"
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.editar"
            ]
        }

        return self.model.objects.all()




    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(user__email__icontains=search) | Q(user__first_name__icontains=search) | \
                Q(user__last_name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Actualizar permisos de la cuenta">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'departamento':
            return row.departamento.nombre

        elif column == 'users':
            return row.users.all().count()

        else:
            return super(PermisosProyectosListApi, self).render_column(row, column)



class UsuariosAutocomplete(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.User.objects.none()

        qs = models.User.objects.all()

        if self.q:
            q = Q(email__icontains = self.q) | Q(first_name__icontains = self.q) | Q(last_name__icontains = self.q)
            qs = qs.filter(q)

        return qs

class RutasAutocomplete(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Rutas.objects.none()

        qs = models.Rutas.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs

#------------------------------------- SOPORTES -------------------------------------

class SoportesHogaresListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','segundo_apellido']
    order_columns = ['id','documento','primer_nombre','municipio','segundo_apellido']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.soportes.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver componentes">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)

        elif column == 'segundo_apellido':
            return '<div class="center-align">' + str(row.get_cantidad_instrumentos()) + '</div>'

        else:
            return super(SoportesHogaresListApi, self).render_column(row, column)


class SoportesHogaresComponenteListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','nombre','consecutivo','momentos']
    order_columns = ['id','nombre','consecutivo','momentos']

    def get_initial_queryset(self):

        self.hogar = models.Hogares.objects.get(id = self.kwargs['pk_hogar'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.soportes.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="componente/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver momentos">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'

        elif column == 'momentos':
            return '<div class="center-align">' + str(row.get_cantidad_instrumentos(self.hogar)) + '</div>'

        else:
            return super(SoportesHogaresComponenteListApi, self).render_column(row, column)


class SoportesHogaresMomentosListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id','nombre','consecutivo','novedades']
    order_columns = ['id','nombre','consecutivo','novedades']

    def get_initial_queryset(self):

        self.hogar = models.Hogares.objects.get(id = self.kwargs['pk_hogar'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.soportes.ver"
            ]
        }
        return self.model.objects.filter(componente = self.componente)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="instrumento/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.get_consecutivo()) + '</b></div>'

        elif column == 'novedades':
            return '<div class="center-align">' + str(row.get_cantidad_instrumentos(self.hogar,self.componente)) + '</div>'




        else:
            return super(SoportesHogaresMomentosListApi, self).render_column(row, column)


class SoportesHogaresInstrumentosListApi(BaseDatatableView):
    model = models.InstrumentosRutaObject
    columns = ['id','ruta','consecutivo']
    order_columns = ['id','ruta','consecutivo']

    def get_initial_queryset(self):

        self.hogar = models.Hogares.objects.get(id = self.kwargs['pk_hogar'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.soportes.ver"
            ]
        }
        return self.model.objects.filter(hogar = self.hogar,momento=self.momento)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soporte">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'ruta':
            return row.instrumento.nombre


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.instrumento.get_consecutivo()) + '</b></div>'


        else:
            return super(SoportesHogaresInstrumentosListApi, self).render_column(row, column)


#------------------------------------- cortes -------------------------------------

class CortesListApi(BaseDatatableView):
    model = models.Cortes
    columns = ['id','consecutivo','creation','descripcion','corte','usuario_creacion','valor']
    order_columns = ['id','consecutivo','creation','descripcion','corte','usuario_creacion','valor']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cuentas_cobro.ver",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(descripcion__icontains=search) | Q(consecutivo=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro corte {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'corte':
            return '<div class="center-align"><b>' + str(row.get_cantidad_cuentas_cobro()) + '</b></div>'

        elif column == 'usuario_creacion':
            novedad = row.get_novedades()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'valor':
            return '<b>${:20,.2f}</b>'.format(row.get_valor())

        else:
            return super(CortesListApi, self).render_column(row, column)


class CortesCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['id','html','ruta','creation','estado','delta','usuario_creacion','data_json','valores_json','file','file2']
    order_columns = ['id','html','ruta','creation','estado','delta','usuario_creacion','data_json','valores_json','file','file2']

    def get_initial_queryset(self):
        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver"
            ],
            "cuentas_cobro_editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.editar"
            ],
            "cuentas_cobro_cargar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.cargar"
            ],
            "cuentas_cobro_estado": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.estado"
            ]
        }
        return self.model.objects.filter(corte__id = self.kwargs['pk_corte'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(ruta__nombre__icontains=search) | Q(ruta__contrato__nombre__icontains=search) | \
                Q(ruta__contrato__contratista__nombres__icontains=search) | Q(ruta__contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('cuentas_cobro_editar')) and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar cuenta de cobro {1}">' \
                                '<i class="material-icons">build</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.ruta.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">build</i>' \
                       '</div>'

            return ret

        elif column == 'html':
            if self.request.user.has_perms(self.permissions.get('cuentas_cobro_cargar')) and row.estado != 'Creado' and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                                '<i class="material-icons">cloud_upload</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.ruta.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'

            return ret

        elif column == 'ruta':
            return '<div class="center-align"><b>' + str(row.ruta.nombre) + '</b></div>'

        elif column == 'creation':
            return '{0} - {1}'.format(row.ruta.contrato.nombre,row.ruta.contrato.contratista)

        elif column == 'estado':

            if self.request.user.is_superuser:

                ret = '<div class="center-align">' \
                            '<a href="estado/{0}/">' \
                                '<span><b>{1}</b></span>' \
                            '</a>' \
                      '</div>'.format(row.id, row.estado)

            elif self.request.user.has_perms(self.permissions.get('cuentas_cobro_estado')) and row.estado != 'Generado' and row.estado != 'Creado' and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                      '<a href="estado/{0}/">' \
                      '<span><b>{1}</b></span>' \
                      '</a>' \
                      '</div>'.format(row.id, row.estado)

            else:
                ret = '<div class="center-align">' \
                            '<span>{1}</span>' \
                      '</div>'.format(row.id, row.estado)

            return ret

        elif column == 'delta':
            if row.estado == 'Cargado':
                return '<span class="new badge" data-badge-caption="">1</span>'
            elif row.estado =="Reportado":
                return '<div class="center-align">' \
                            '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Reportado por: {0}">' \
                                '<i class="material-icons">verified_user</i>' \
                            '</a>' \
                      '</div>'.format(row.usuario_actualizacion.get_full_name_string())
            else:
                return ''

        elif column == 'usuario_creacion':
            return '<b>${:20,.2f}</b>'.format(row.valor.amount)

        elif column == 'data_json':
            return row.ruta.contrato.inicio

        elif column == 'valores_json':
            return row.ruta.contrato.fin

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file2(),'Descargar archivo')
            else:
                ret = ''

            return ret

        else:
            return super(CortesCuentasCobroListApi, self).render_column(row, column)


# ------------------------------- CUENTAS DE COBRO ----------------------------------

class RutasCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['corte', 'creation', 'valor', 'estado', 'file', 'file2', 'html']
    order_columns = ['corte', 'creation', 'valor', 'estado', 'file', 'file2', 'html']

    def get_initial_queryset(self):
        return self.model.objects.filter(ruta__id=self.kwargs['pk_ruta'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(corte__consecutivo=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ],
            "cargar_cuentas_cobro": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.cuentas_cobro.cargar"
            ]
        }

        if column == 'corte':
            if row.corte != None:
                return '<div class="center-align"><b>' + str(row.corte.consecutivo) + '</b></div>'
            else:
                return 'Liquidación'

        elif column == 'creation':
            return '<div>' + row.pretty_creation_datetime() + '</div>'

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format('{:20,.2f}'.format(row.valor.amount))

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                      '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a>' \
                      '</div>'.format(row.url_file(), 'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                      '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a>' \
                      '</div>'.format(row.url_file2(), 'Descargar archivo')
            else:
                ret = ''

            return ret


        elif column == 'estado':
            if row.estado == 'Pendiente':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<b>{0}</b>' \
                      '</a>' \
                      '</div>'.format(row.estado, row.observaciones)
            else:
                ret = row.estado

            return ret


        elif column == 'html':
            ret = '<div class="center-align">' \
                  '<a href="detalle/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                  '<i class="material-icons">assignment_turned_in</i>' \
                  '</a>' \
                  '</div>'.format(row.id, 'Detalle de las actividades')
            return ret

        else:
            return super(RutasCuentasCobroListApi, self).render_column(row, column)


class CorteHogaresActividadesListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo']
    order_columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id = self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }
        ids = models.CuposRutaObject.objects.filter(ruta = self.ruta,corte = self.cuenta_cobro.corte).values_list('momento__id',flat = True)
        return self.model.objects.filter(id__in = ids)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(consecutivo__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            if row.tipo in ['vinculacion','visita','encuentro','otros']:
                url = 'hogares'
            else:
                url = 'instrumentos'

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="{1}/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver hogares y/o instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,url)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)

        elif column == 'tipo':
            nombre = ''
            color = ''
            icono = ''

            if row.tipo == 'vinculacion':
                nombre = 'Vinculación'
                color = '#558b2f'
                icono = 'accessibility'

            elif row.tipo == 'visita':
                nombre = 'Visita'
                color = '#e65100'
                icono = 'account_balance'

            elif row.tipo == 'encuentro':
                nombre = 'Encuentro'
                color = '#5d4037'
                icono = 'camera'

            else:
                nombre = 'Otros'
                color = '#37474f'
                icono = 'dashboard'

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                   '<i style = "color:{1};" class="material-icons">{2}</i>' \
                   '</a>' \
                   '</div>'.format(nombre, color,icono)


        elif column == 'valor_maximo':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_maximo_momento_corte(self.ruta,self.cuenta_cobro.corte))




        else:
            return super(CorteHogaresActividadesListApi, self).render_column(row, column)


class CorteActividadesHogaresRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','id_elegible','telefono']
    order_columns = ['id','documento','primer_nombre','municipio','id_elegible','telefono']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])


        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, corte=self.cuenta_cobro.corte, momento = self.momento).values_list('hogar__id', flat=True)
        return self.model.objects.filter(id__in=ids)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los instrumentos de la visita">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)


        elif column == 'id_elegible':
            return row.get_estado_valor(self.ruta,self.momento)

        elif column == 'telefono':
            return row.get_estado(self.ruta,self.momento)

        else:
            return super(CorteActividadesHogaresRutasListApi, self).render_column(row, column)


class CorteInstrumentosHogaresRutasListApi(BaseDatatableView):
    model = models.InstrumentosRutaObject
    columns = ['creacion','id','consecutivo', 'nombre', 'estado']
    order_columns = ['creacion','id', 'consecutivo', 'nombre', 'estado']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        return self.model.objects.filter(ruta=self.ruta, momento=self.momento, hogar=self.hogar)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,utils.pretty_datetime(timezone.localtime(row.fecha_actualizacion)))

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="trazabilidad/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">class</i>' \
                      '</a>' \
                      '</div>'.format(row.id, 'Ver la trazabilidad')

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">class</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)


        elif column == 'nombre':
            return row.nombre


        elif column == 'estado':
            ret = ''
            if row.estado == 'cargado':
                ret = ''
            return row.estado


        else:
            return super(CorteInstrumentosHogaresRutasListApi, self).render_column(row, column)


class CorteInstrumentosHogaresRutasTrazabilidadListApi(BaseDatatableView):
    model = models.InstrumentosTrazabilidadRutaObject
    columns = ['creacion','user','observacion']
    order_columns = ['creacion','user','observacion']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])


        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        return self.model.objects.filter(instrumento=self.instrumento_object)



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            return timezone.localtime(row.creacion).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'user':
            return row.user.get_full_name()


        else:
            return super(CorteInstrumentosHogaresRutasTrazabilidadListApi, self).render_column(row, column)



class MisRutasCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['id','corte','creation','valor','estado','file','file2','valores_json']
    order_columns = ['id','corte','creation','valor','estado','file','file2','valores_json']

    def get_initial_queryset(self):
        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta']).exclude(estado = 'Creado')


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(corte__consecutivo=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):




        if column == 'id':

            if row.corte != None:
                consecutivo = row.corte.consecutivo
            else:
                consecutivo = 'Liquidación'


            if self.request.user.has_perms(self.permissions.get('all')) and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="cargar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro Corte {1}">' \
                                '<i class="material-icons">cloud_upload</i>' \
                           '</a>' \
                       '</div>'.format(row.id,consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'

            return ret

        if column == 'corte':
            if row.corte != None:
                return '<div class="center-align"><b>' + str(row.corte.consecutivo) + '</b></div>'
            else:
                return 'Liquidación'

        elif column == 'creation':
            return '<div>' + row.pretty_creation_datetime() + '</div>'

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format('{:20,.2f}'.format(row.valor.amount))

        elif column == 'estado':
            ret = ''

            if row.estado == 'Reportado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="La cuenta de cobro se reporto para pago">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Cargado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="La cuenta de cobro se encuentra en revisión">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Generado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Por favor firma y carga la cuenta de cobro">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Pendiente':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado,row.observaciones)

            return ret

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file2(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'valores_json':
            ret = '<div class="center-align">' \
                        '<a href="detalle/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<i class="material-icons">assignment</i>' \
                        '</a>' \
                  '</div>'.format(row.id,'Ver detalle de actividades')

            return ret

        else:
            return super(MisRutasCuentasCobroListApi, self).render_column(row, column)


class MisCorteHogaresActividadesListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo']
    order_columns = ['id', 'consecutivo', 'nombre', 'tipo', 'valor_maximo']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id = self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }
        ids = models.CuposRutaObject.objects.filter(ruta = self.ruta,corte = self.cuenta_cobro.corte).values_list('momento__id',flat = True)
        return self.model.objects.filter(id__in = ids)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(consecutivo__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''

            if row.tipo in ['vinculacion','visita','encuentro','otros']:
                url = 'hogares'
            else:
                url = 'instrumentos'

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="{1}/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver hogares y/o instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,url)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)

        elif column == 'tipo':
            nombre = ''
            color = ''
            icono = ''

            if row.tipo == 'vinculacion':
                nombre = 'Vinculación'
                color = '#558b2f'
                icono = 'accessibility'

            elif row.tipo == 'visita':
                nombre = 'Visita'
                color = '#e65100'
                icono = 'account_balance'

            elif row.tipo == 'encuentro':
                nombre = 'Encuentro'
                color = '#5d4037'
                icono = 'camera'

            else:
                nombre = 'Otros'
                color = '#37474f'
                icono = 'dashboard'

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                   '<i style = "color:{1};" class="material-icons">{2}</i>' \
                   '</a>' \
                   '</div>'.format(nombre, color,icono)


        elif column == 'valor_maximo':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_maximo_momento_corte(self.ruta,self.cuenta_cobro.corte))




        else:
            return super(MisCorteHogaresActividadesListApi, self).render_column(row, column)


class MisCorteActividadesHogaresRutasListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','id_elegible','telefono']
    order_columns = ['id','documento','primer_nombre','municipio','id_elegible','telefono']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])


        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }

        ids = models.CuposRutaObject.objects.filter(ruta=self.ruta, corte=self.cuenta_cobro.corte, momento = self.momento).values_list('hogar__id', flat=True)
        return self.model.objects.filter(id__in=ids)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | \
                Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instrumentos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los instrumentos de la visita">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':

            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)


        elif column == 'id_elegible':
            return row.get_estado_valor(self.ruta,self.momento)

        elif column == 'telefono':
            return row.get_estado(self.ruta,self.momento)

        else:
            return super(MisCorteActividadesHogaresRutasListApi, self).render_column(row, column)


class MisCorteInstrumentosHogaresRutasListApi(BaseDatatableView):
    model = models.InstrumentosRutaObject
    columns = ['creacion','id','consecutivo', 'nombre', 'estado']
    order_columns = ['creacion','id', 'consecutivo', 'nombre', 'estado']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }

        return self.model.objects.filter(ruta=self.ruta, momento=self.momento, hogar=self.hogar)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,utils.pretty_datetime(timezone.localtime(row.fecha_actualizacion)))

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="trazabilidad/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">class</i>' \
                      '</a>' \
                      '</div>'.format(row.id, 'Ver la trazabilidad')

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">class</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)


        elif column == 'nombre':
            return row.nombre


        elif column == 'estado':
            ret = ''
            if row.estado == 'cargado':
                ret = ''
            return row.estado


        else:
            return super(MisCorteInstrumentosHogaresRutasListApi, self).render_column(row, column)


class MisCorteInstrumentosHogaresRutasTrazabilidadListApi(BaseDatatableView):
    model = models.InstrumentosTrazabilidadRutaObject
    columns = ['creacion','user','observacion']
    order_columns = ['creacion','user','observacion']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])


        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }

        return self.model.objects.filter(instrumento=self.instrumento_object)



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            return timezone.localtime(row.creacion).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'user':
            return row.user.get_full_name()


        else:
            return super(MisCorteInstrumentosHogaresRutasTrazabilidadListApi, self).render_column(row, column)





class RuteoHogaresListApi(BaseDatatableView):
    model = models.Hogares
    columns = ['id','documento','primer_nombre','municipio','id_elegible','id_archivo','ruta_vinculacion','puntaje_sisben','folio']
    order_columns = ['id','documento','primer_nombre','municipio','id_elegible','id_archivo','ruta_vinculacion','puntaje_sisben','folio']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.ruteo.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(primer_nombre__icontains=search) | Q(segundo_nombre__icontains=search) | \
                Q(primer_apellido__icontains=search) | Q(segundo_apellido__icontains=search) | Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                      '<a href="{0}/componentes/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver componentes del hogar {1}">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                  '</div>'.format(row.id, row.documento)
            return ret

        elif column == 'documento':
            return '<div class="center-align"><b>' + str(row.documento) + '</b></div>'

        elif column == 'primer_nombre':
            return row.get_gull_name()

        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)

        elif column == 'id_archivo':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_total())

        elif column == 'id_elegible':
            return '<div class="center-align">{0}</div>'.format(row.get_cantidad_componentes())

        elif column == 'ruta_vinculacion':
            return '<div class="center-align">{0}</div>'.format(row.get_nombre_ruta_vinculacion())


        elif column == 'puntaje_sisben':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_vinculacion())



        elif column == 'folio':
            ret = '<div class="center-align">' \
                      '<a href="{0}/cambiar/vinculacion/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cambiar ruta de vinculación del hogar {1}">' \
                            '<i class="material-icons">track_changes</i>' \
                      '</a>' \
                  '</div>'.format(row.id, row.documento)
            return ret


        else:
            return super(RuteoHogaresListApi, self).render_column(row, column)


class RuteoHogaresComponentesListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','nombre','consecutivo','momentos','valor','ruta','valor_pagado']
    order_columns = ['id','nombre','consecutivo','momentos','valor','ruta','valor_pagado']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.ruteo.ver"
            ]
        }
        self.hogar = models.Hogares.objects.get(pk = self.kwargs['pk'])
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/momentos/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver momentos del componente {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'momentos':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_numero_momentos())

        elif column == 'consecutivo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutivo)

        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.get_valor_hogar(self.hogar))


        elif column == 'ruta':
            return '<div class="center-align">{0}</div>'.format(row.get_ruta_hogar_componente(self.hogar))



        elif column == 'valor_pagado':
            ret = '<div class="center-align">' \
                      '<a href="{0}/cambiar/componente/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cambiar ruta del componente {1}">' \
                            '<i class="material-icons">track_changes</i>' \
                      '</a>' \
                  '</div>'.format(row.id, row.nombre)
            return ret


        else:
            return super(RuteoHogaresComponentesListApi, self).render_column(row, column)


class RuteoHogaresMomentosListApi(BaseDatatableView):
    model = models.CuposRutaObject
    columns = ['ruta','tipo','estado','valor','corte','translado']
    order_columns = ['ruta','tipo','estado','valor','corte','translado']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.ruteo.ver"
            ]
        }
        self.hogar = models.Hogares.objects.get(pk = self.kwargs['pk'])
        self.componente = models.Componentes.objects.get(id = self.kwargs['pk_componente'])
        return self.model.objects.filter(momento__componente=self.componente,hogar=self.hogar)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):


        if column == 'ruta':
            return '<div class="center-align">{0}</div>'.format(row.ruta.nombre)


        elif column == 'tipo':
            return '<div class="center-align">{0}</div>'.format(row.momento.nombre)


        elif column == 'corte':
            return '<div class="center-align">{0}</div>'.format(row.corte.consecutivo if row.corte != None else '')

        elif column == 'valor':
            return '<div class="center-align">$ {:20,.2f}</div>'.format(row.valor.amount)


        else:
            return super(RuteoHogaresMomentosListApi, self).render_column(row, column)



class CambioRutasAutocomplete(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Rutas.objects.none()

        qs = models.Rutas.objects.exclude(id = self.kwargs['pk_ruta']).filter(componente__id = self.kwargs['pk_componente'])

        if self.q:
            q = Q(nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs



class CambioRutasAutocompleteVinculacion(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Rutas.objects.none()

        qs = models.Rutas.objects.exclude(id = self.kwargs['pk_ruta'])

        if self.q:
            q = Q(nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs





class CambioRutasAutocompleteAll(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Rutas.objects.none()

        qs = models.Rutas.objects.filter(componente__id = self.kwargs['pk_componente'])

        if self.q:
            q = Q(nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs



class CambioRutasAutocompleteVinculacionAll(autocomplete.Select2QuerySetView):


    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Rutas.objects.none()

        qs = models.Rutas.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs




class DirectorioListApi(BaseDatatableView):
    model = models.Contactos
    columns = ['id','nombres','apellidos','municipio','cargo','celular']
    order_columns = ['id','nombres','apellidos','municipio','cargo','celular']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.directorio.ver"
            ],
            "editar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.directorio.ver",
                "usuarios.fest_2019.directorio.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombres__icontains=search) | Q(apellidos__icontains=search) | \
                Q(municipio__nombre__icontains=search) | Q(cargo__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar contacto">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret


        elif column == 'municipio':
            return '{0}, {1}'.format(row.municipio.nombre,row.municipio.departamento.nombre)


        else:
            return super(DirectorioListApi, self).render_column(row, column)