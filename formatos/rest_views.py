from django_datatables_view.base_datatable_view import BaseDatatableView
from formatos import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class Level1ListApi(BaseDatatableView):
    model = models.Level1
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level1ListApi, self).render_column(row, column)

class Level2ListApi(BaseDatatableView):
    model = models.Level2
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']


    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l1'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level2ListApi, self).render_column(row, column)

class Level3ListApi(BaseDatatableView):
    model = models.Level3
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l2'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level3ListApi, self).render_column(row, column)

class Level4ListApi(BaseDatatableView):
    model = models.Level4
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l3'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level4ListApi, self).render_column(row, column)

class Level5ListApi(BaseDatatableView):
    model = models.Level5
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l4'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level5ListApi, self).render_column(row, column)

class Level6ListApi(BaseDatatableView):
    model = models.Level6
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']


    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l5'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level6ListApi, self).render_column(row, column)

class Level7ListApi(BaseDatatableView):
    model = models.Level7
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l6'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            if row.nivel == True:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contenido de {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">add</i>' \
                          '</a>'.format(row.id, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level7ListApi, self).render_column(row, column)

class Level8ListApi(BaseDatatableView):
    model = models.Level8
    columns = ['id','consecutivo','nombre','file']
    order_columns = ['id','consecutivo','nombre','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(level__id = self.kwargs['pk_l7'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.formatos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + row.get_consecutivo() + '</b></div>'



        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_link</i>' \
                          '</a>'.format(row.url, row.nombre)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(Level8ListApi, self).render_column(row, column)