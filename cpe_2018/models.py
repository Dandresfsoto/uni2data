from django.db import models
import uuid
from usuarios.models import User
from django.conf import settings
from pytz import timezone
from storages.backends.ftp import FTPStorage
from recursos_humanos.models import Contratistas, Contratos
from djmoney.models.fields import MoneyField
import json
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from config.extrafields import ContentTypeRestrictedFileField
from delta import html
from cpe_2018 import tasks
from bs4 import BeautifulSoup
import html2text


fs = FTPStorage()

settings_time_zone = timezone(settings.TIME_ZONE)
# Create your models here.

class Regiones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_departamentos = models.IntegerField(default=0)
    cantidad_municipios = models.IntegerField(default=0)
    cantidad_radicados = models.IntegerField(default=0)
    cantidad_docentes = models.IntegerField(default=0)
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    def get_cantidad_departamentos(self):
        return Departamentos.objects.filter(region__id = self.id).count()

    def get_cantidad_municipios(self):
        return Municipios.objects.filter(departamento__region__id = self.id).count()

    def get_cantidad_radicados(self):
        return Radicados.objects.filter(municipio__departamento__region__id = self.id).count()

    def get_cantidad_docentes(self):
        return Docentes.objects.filter(municipio__departamento__region__id = self.id).count()

class Departamentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    region = models.ForeignKey(Regiones, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_municipios = models.IntegerField(default=0)
    cantidad_radicados = models.IntegerField(default=0)
    cantidad_docentes = models.IntegerField(default=0)
    alias_simec = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.nombre

    def get_cantidad_municipios(self):
        return Municipios.objects.filter(departamento__id = self.id).count()

    def get_cantidad_radicados(self):
        return Radicados.objects.filter(municipio__departamento__id = self.id).count()

    def get_cantidad_docentes(self):
        return Docentes.objects.filter(municipio__departamento__id = self.id).count()

class Municipios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    departamento = models.ForeignKey(Departamentos,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_radicados = models.IntegerField(default=0)
    cantidad_docentes = models.IntegerField(default=0)
    latitud = models.DecimalField(max_digits=9,decimal_places=6,blank=True,null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6,blank=True,null=True)
    alias_simec = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.nombre,self.departamento.nombre)

    def get_cantidad_radicados(self):
        return Radicados.objects.filter(municipio__id = self.id).count()

    def get_cantidad_docentes(self):
        return Docentes.objects.filter(municipio__id = self.id).count()

def upload_dinamic_rutas(instance, filename):
    return '/'.join(['Acceso - CPE', 'Rutas', str(instance.id), filename])

class Rutas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_ruta", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_ruta",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    region = models.ForeignKey(Regiones,on_delete=models.DO_NOTHING)
    nombre = models.CharField(unique=True,max_length=100)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP',default=0)
    estado = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_rutas, blank=True, null=True)
    contrato = models.ForeignKey(Contratos,on_delete=models.DO_NOTHING,blank=True,null=True)

    actividades_json = models.CharField(max_length=500,blank=True, null=True)
    cuentas_cobro_json = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)



    def get_liquidacion(self):

        liquidacion = None

        try:
            liquidacion = Liquidaciones.objects.get(ruta = self)
        except:
            pass

        return liquidacion


    def actualizar_valores_acceso(self):

        actividades_ruta = json.loads(self.actividades_json)
        actividades_formacion = actividades_ruta['componente_' + str(Componentes.objects.get(numero='2').id)]
        peso_formacion = actividades_ruta['peso_' + str(Componentes.objects.get(numero='2').id)]
        cantidad_retomas = 0
        valor_retomas = 0
        valor_contrato = float(self.contrato.valor.amount)

        for entregable in Entregables.objects.filter(tipo='ruta&estrategia'):
            cantidad_retomas += int(actividades_ruta['entregable_{0}'.format(entregable.id)])
            valor_retomas += actividades_ruta['valor_{0}'.format(entregable.id)]

        valor_formacion = float((valor_contrato * peso_formacion) / 100.0)

        valor_dividir = valor_contrato - cantidad_retomas * valor_retomas - valor_formacion

        entregables = EntregableRutaObject.objects.filter(entregable__tipo__in=['sede', 'sede&ruta'], ruta=self)
        peso_total = entregables.aggregate(Sum('entregable__peso'))['entregable__peso__sum']

        if peso_total == None:
            peso_total = 0

        if peso_total > 0:

            valor_unidad = valor_dividir / peso_total

            for entregable in EntregableRutaObject.objects.filter(entregable__tipo__in=['sede', 'sede&ruta'], ruta=self):
                entregable.valor = valor_unidad * entregable.entregable.peso
                entregable.save()

        else:
            pass


        if actividades_formacion > 0:

            objetos_formacion_asignados = EntregableRutaObject.objects.filter(entregable = None, ruta = self,tipo = 'Docente', valor = 0)

            objetos_formacion_sin_asignar = EntregableRutaObject.objects.filter(entregable=None, ruta=self, tipo='Docente').exclude(id__in = objetos_formacion_asignados.values_list('id',flat=True))

            entregables_formacion = Entregables.objects.filter(momento__estrategia__numero__in=[1,2], tipo='docente')


            docentes_grupos = Docentes.objects.filter(grupo__ruta = self)

            objetos_creados_docentes = EntregableRutaObject.objects.filter(entregable__in=entregables_formacion, ruta=self,docente__in=docentes_grupos)

            objetos_creados_docentes.delete()

            objetos_formacion_asignados.update(valor = 0, estado = "asignado")

            objetos_formacion_sin_asignar.update(valor=0, estado="asignado")



            objetos_formacion_sin_asignar = EntregableRutaObject.objects.filter(entregable=None, ruta=self, tipo='Docente')



            valor_docente = valor_formacion / objetos_formacion_sin_asignar.count()

            objetos_formacion_sin_asignar.update(valor = valor_docente)




            for docente in docentes_grupos:

                objetos_formacion = EntregableRutaObject.objects.filter(
                    entregable=None,
                    ruta=self,
                    padre='docente&{0}'.format(self.id),
                    estado='asignado',
                    tipo='Docente'
                )
                objeto_formacion = objetos_formacion.first()

                valor_docente = objeto_formacion.valor.amount

                if docente.grupo.estrategia.numero == 1:
                    entregables = Entregables.objects.filter(momento__estrategia__numero=1, tipo='docente')
                else:
                    entregables = Entregables.objects.filter(momento__estrategia__numero=2, tipo='docente')

                cantidad = entregables.aggregate(Sum('peso'))['peso__sum']

                if cantidad == None:
                    cantidad = 0

                if cantidad > 0:
                    valor_entregable = valor_docente / cantidad
                else:
                    valor_entregable = 0

                for entregable in entregables:

                    q = EntregableRutaObject.objects.filter(
                        entregable=entregable,
                        padre='docente&{0}&{1}'.format(docente.grupo.ruta.id, docente.grupo.id),
                        ruta=docente.grupo.ruta,
                        tipo='Docente',
                        docente=docente
                    )

                    if q.count() == 0:
                        EntregableRutaObject.objects.create(
                            entregable=entregable,
                            ruta=docente.grupo.ruta,
                            valor=valor_entregable * entregable.peso,
                            estado='asignado',
                            padre='docente&{0}&{1}'.format(
                                docente.grupo.ruta.id,
                                docente.grupo.id
                            ),
                            tipo='Docente',
                            orden=entregable.orden,
                            docente=docente
                        )

                objeto_formacion.valor = 0
                objeto_formacion.estado = 'Pagado'
                objeto_formacion.save()
                docente.grupo = docente.grupo
                docente.save()

        else:
            pass

        return 'Actualizada la ruta: {0}'.format(self.nombre)




    def cerrar_ruta(self):
        self.cerrar_objetos_sede_ruta()
        self.cerrar_objetos_ruta_estrategia()
        self.cerrar_objetos_ruta_formacion()
        self.cerrar_grupos_formacion()
        self.cerrar_radicados()
        return None

    def abrir_ruta(self):
        self.abrir_objetos_sede_ruta()
        self.abrir_objetos_ruta_estrategia()
        self.abrir_objetos_ruta_formacion()
        self.abrir_radicados()
        return None

    def cerrar_objetos_sede_ruta(self):
        query = EntregableRutaObject.objects.filter(padre='sede&ruta&{0}'.format(self.id), estado='asignado')
        query.update(estado = "Cerrado")
        return None

    def abrir_objetos_sede_ruta(self):
        query = EntregableRutaObject.objects.filter(padre='sede&ruta&{0}'.format(self.id), estado='Cerrado')
        query.update(estado = "asignado")
        return None



    def cerrar_objetos_ruta_estrategia(self):
        query = EntregableRutaObject.objects.filter(padre='ruta&estrategia&{0}'.format(self.id), estado='asignado')
        query.update(estado = "Cerrado")
        return None

    def abrir_objetos_ruta_estrategia(self):
        query = EntregableRutaObject.objects.filter(padre='ruta&estrategia&{0}'.format(self.id), estado='Cerrado')
        query.update(estado = "asignado")
        return None



    def cerrar_objetos_ruta_formacion(self):
        query = EntregableRutaObject.objects.filter(padre = "docente&{0}".format(self.id), tipo = "Docente", entregable = None, estado='asignado')
        query.update(estado = "Cerrado")
        return None

    def abrir_objetos_ruta_formacion(self):
        query = EntregableRutaObject.objects.filter(padre = "docente&{0}".format(self.id), tipo = "Docente", entregable = None, estado='Cerrado')
        query.update(estado = "asignado")
        return None


    def cerrar_grupos_formacion(self):
        for grupo in Grupos.objects.filter(ruta = self):
            for docente in Docentes.objects.filter(grupo = grupo):
                EntregableRutaObject.objects.filter(
                    ruta=self,
                    estado='asignado',
                    padre='docente&{0}&{1}'.format(self.id,grupo.id),
                    tipo='Docente',
                    docente=docente
                ).update(estado = "Cerrado")

                docente.grupo = None
                docente.save()
        return None



    def cerrar_radicados(self):
        for radicado in Radicados.objects.filter(ruta = self):
            EntregableRutaObject.objects.filter(ruta=self,estado='asignado',padre='sede&{0}'.format(radicado.id),tipo='Radicado',radicado=radicado).update(estado = "Cerrado")
            radicado.ruta = None
            radicado.save()
        return None


    def abrir_radicados(self):
        for radicado in Radicados.objects.filter(ruta = self):
            EntregableRutaObject.objects.filter(ruta=self,estado='Cerrado',padre='sede&{0}'.format(radicado.id),tipo='Radicado',radicado=radicado).update(estado = "asignado")
            radicado.ruta = None
            radicado.save()
        return None




    def get_valor_promedio_radicados(self):
        entregables_sede = Entregables.objects.filter(tipo = 'sede')
        objetos_radicados = EntregableRutaObject.objects.filter(ruta = self, entregable__tipo='sede')
        valor_objetos = objetos_radicados.aggregate(Sum('valor'))['valor__sum']
        radicados = Radicados.objects.filter(ruta = self).count()

        if valor_objetos == None:
            valor_objetos = 0

        if radicados == 0:
            return 0
        else:
            return valor_objetos/radicados

    def get_valor_promedio_docentes(self):
        entregables_docentes = EntregableRutaObject.objects.filter(padre="docente&{0}".format(self.id))
        valor_objetos = entregables_docentes.aggregate(Sum('valor'))['valor__sum']

        if valor_objetos == None:
            valor_objetos = 0

        actividades_json = json.loads(self.actividades_json)
        cantidad = actividades_json['componente_' + str(Componentes.objects.get(numero='2').id)]

        if cantidad == 0:
            return 0
        else:
            return valor_objetos/cantidad

    def get_valor_promedio_retomas(self):
        entregables_retoma = EntregableRutaObject.objects.filter(ruta=self, padre="ruta&estrategia&{0}".format(self.id))
        valor_objetos = entregables_retoma.aggregate(Sum('valor'))['valor__sum']

        if valor_objetos == None:
            valor_objetos = 0

        actividades_json = json.loads(self.actividades_json)
        cantidad = 0

        for entregable in Entregables.objects.filter(tipo='ruta&estrategia'):
            cantidad += actividades_json['entregable_{0}'.format(entregable.id)]

        if cantidad == 0:
            return 0
        else:
            return valor_objetos / cantidad

    def get_valor_entregables_ruta(self):

        q = Q(padre = "sede&ruta&{0}".format(self.id)) | Q(padre = "sede&ruta&siformacion&{0}".format(self.id))
        entregables_retoma = EntregableRutaObject.objects.filter(ruta=self).filter(q)
        valor_objetos = entregables_retoma.aggregate(Sum('valor'))['valor__sum']

        if valor_objetos == None:
            valor_objetos = 0


        return valor_objetos

    def update_objects(self):

        self.clean_objects()

        for radicado in Radicados.objects.filter(ruta = self):
            radicado.objetos_radicado(ruta = self, valor = None)

        if Radicados.objects.filter(ruta = self).count() > 0:
            self.objetos_sede_ruta(valor = None)

        self.objetos_ruta_estrategia()
        self.objetos_ruta_si_formacion(valor = None)
        self.objetos_formacion(valor = None)
        self.objetos_servicio_zona(valor=None)

        valor_objetos_ruta_estrategia = EntregableRutaObject.objects.filter(padre="ruta&estrategia&{0}".format(self.id)).aggregate(Sum('valor'))['valor__sum']

        valor_componentes = self.calcular_valores_componentes(valor_objetos_ruta_estrategia)

        for key in valor_componentes.keys():
            self.asignar_valor_entregable_componente(valor_componentes[key],key)

        return None

    def clean_objects(self):

        radicados_ids = []

        for id in Radicados.objects.filter(ruta = self).values_list('id',flat=True):
            radicados_ids.append('sede&{0}'.format(id))

        EntregableRutaObject.objects.filter(ruta = self, estado__in = ['disponible','asignado'], padre__in=radicados_ids).delete()

        EntregableRutaObject.objects.filter(ruta = self, estado__in = ['disponible','asignado'], padre="sede&ruta&{0}".format(self.id)).delete()

        EntregableRutaObject.objects.filter(ruta=self, estado__in = ['disponible','asignado'], padre="sede&ruta&siformacion&{0}".format(self.id)).delete()

        EntregableRutaObject.objects.filter(ruta=self, estado__in = ['disponible','asignado'],padre="docente&{0}".format(self.id)).delete()

        EntregableRutaObject.objects.filter(ruta=self, estado__in = ['disponible','asignado'],padre="servicio&{0}".format(self.id)).delete()

        return None

    def objetos_sede_ruta(self, valor):

        for entregable in Entregables.objects.filter(tipo='sede&ruta'):

            query = EntregableRutaObject.objects.filter(
                entregable = entregable,
                padre='sede&ruta&{0}'.format(self.id)
            )

            if query.count() == 0:
                EntregableRutaObject.objects.create(
                    entregable = entregable,
                    ruta = self,
                    valor = valor,
                    estado = 'asignado',
                    padre = 'sede&ruta&{0}'.format(self.id),
                    orden = entregable.orden,
                    tipo = "Ruta"
                )

            elif query.count() == 1:
                obj = query[0]

                if obj.estado == 'disponible':
                    query.update(
                        ruta = self,
                        valor = valor,
                        estado = 'asignado',
                        orden = entregable.orden,
                        tipo = "Ruta"
                    )

            else:
                raise ValueError(
                    'No debe existir mas de un objeto para el entregable {0} de la ruta {1}'.format(
                        entregable.id,
                        self.id
                    )
                )

        return None

    def objetos_ruta_estrategia(self):

        actividades_json = json.loads(self.actividades_json)

        for entregable in Entregables.objects.filter(tipo='ruta&estrategia'):

            cantidad = actividades_json['entregable_{0}'.format(entregable.id)]
            valor = actividades_json['valor_{0}'.format(entregable.id)]

            EntregableRutaObject.objects.filter(ruta=self, estado__in = ['disponible','asignado'], entregable = entregable, padre="ruta&estrategia&{0}".format(self.id)).delete()
            entregables = EntregableRutaObject.objects.filter(ruta=self, padre="ruta&estrategia&{0}".format(self.id))

            if entregables.count() > cantidad:
                raise ValueError(
                    'No se puede reducir la meta del entregable {0}'.format(entregable.id)
                )

            else:
                for i in range(0,cantidad-entregables.count()):
                    EntregableRutaObject.objects.create(
                        entregable=entregable,
                        ruta=self,
                        valor=valor,
                        estado='asignado',
                        padre='ruta&estrategia&{0}'.format(self.id),
                        orden=entregable.orden,
                        tipo="Ruta retoma"
                    )

        return None

    def objetos_ruta_si_formacion(self, valor):

        actividades_json = json.loads(self.actividades_json)
        cantidad = actividades_json['componente_' + str(Componentes.objects.get(numero = '2').id)]

        if cantidad > 0 and Radicados.objects.filter(ruta = self).count() > 0:
            for entregable in Entregables.objects.filter(tipo='sede&ruta&siformacion'):

                query = EntregableRutaObject.objects.filter(
                    entregable=entregable,
                    padre='sede&ruta&siformacion&{0}'.format(self.id)
                )

                if query.count() == 0:
                    EntregableRutaObject.objects.create(
                        entregable=entregable,
                        ruta=self,
                        valor=valor,
                        estado='asignado',
                        padre='sede&ruta&siformacion&{0}'.format(self.id),
                        orden = entregable.orden,
                        tipo = "Ruta"
                    )

                elif query.count() == 1:
                    obj = query[0]

                    if obj.estado == 'disponible':
                        query.update(
                            ruta=self,
                            valor=valor,
                            estado='asignado',
                            orden=entregable.orden,
                            tipo="Ruta"
                        )

                else:
                    raise ValueError(
                        'No debe existir mas de un objeto para el entregable {0} de la ruta {1}'.format(
                            entregable.id,
                            self.id
                        )
                    )

        return None

    def objetos_formacion(self, valor):

        actividades_json = json.loads(self.actividades_json)
        cantidad = actividades_json['componente_' + str(Componentes.objects.get(numero = '2').id)]
        entregables = EntregableRutaObject.objects.filter(padre = "docente&{0}".format(self.id))

        if cantidad > entregables.count():
            for i in range(0,cantidad-entregables.count()):
                EntregableRutaObject.objects.create(
                    entregable=None,
                    ruta=self,
                    valor=valor,
                    estado='asignado',
                    padre='docente&{0}'.format(self.id),
                    tipo = 'Docente',
                    orden = 2
                )

        return None

    def objetos_servicio_zona(self, valor):

        actividades_json = json.loads(self.actividades_json)
        cantidad = actividades_json['componente_' + str(Componentes.objects.get(numero = '3').id)]
        entregables = EntregableRutaObject.objects.filter(padre = "servicio&{0}".format(self.id))

        if cantidad > entregables.count():
            for i in range(0,cantidad-entregables.count()):
                EntregableRutaObject.objects.create(
                    entregable=None,
                    ruta=self,
                    valor=valor,
                    estado='asignado',
                    padre='servicio&{0}'.format(self.id),
                    tipo = 'Servicio en zona',
                    orden = 1
                )

        return None

    def calcular_valores_componentes(self, valor):

        if valor != None:
            valor_a_dividir = self.contrato.valor.amount - valor
        else:
            valor_a_dividir = self.contrato.valor.amount

        actividades_json = json.loads(self.actividades_json)

        cantidad_docentes = actividades_json['componente_' + str(Componentes.objects.get(numero='2').id)]
        peso_docentes = actividades_json['peso_' + str(Componentes.objects.get(numero='2').id)]

        cantidad_servicios = actividades_json['componente_' + str(Componentes.objects.get(numero='3').id)]
        peso_servicios = actividades_json['peso_' + str(Componentes.objects.get(numero='3').id)]

        peso_sedes = 100 - peso_docentes - peso_servicios

        return {
            '1' : (valor_a_dividir*peso_sedes)/100,
            '2' : (valor_a_dividir*peso_docentes)/100,
            '3' : (valor_a_dividir*peso_servicios)/100
        }

    def asignar_valor_entregable_componente(self, valor, componente):

        if componente == '1':

            radicados_ids = []

            for id in Radicados.objects.filter(ruta=self).values_list('id', flat=True):
                radicados_ids.append('sede&{0}'.format(id))

            q = Q(padre='sede&ruta&siformacion&{0}'.format(self.id)) | \
                Q(padre = 'sede&ruta&{0}'.format(self.id)) | \
                Q(padre__in=radicados_ids)

            query = EntregableRutaObject.objects.filter(q).filter(ruta = self).exclude(estado = ['Cerrado','Pagado','Reportado'])
            cantidad = query.aggregate(Sum('entregable__peso'))['entregable__peso__sum']

            if cantidad == None:
                cantidad = 0

            if cantidad > 0:
                valor_entregable = valor/cantidad
            else:
                valor_entregable = 0

            for q in query:
                q.valor = valor_entregable*q.entregable.peso
                q.save()


        elif componente == '2':
            q = Q(padre='docente&{0}'.format(self.id))

            query = EntregableRutaObject.objects.filter(q)

            if query.count() > 0:
                valor_entregable = valor / query.count()
            else:
                valor_entregable = 0

            query.update(valor=valor_entregable)

        elif componente == '3':
            q = Q(padre='servicio&{0}'.format(self.id))

            query = EntregableRutaObject.objects.filter(q)

            if query.count() > 0:
                valor_entregable = valor / query.count()
            else:
                valor_entregable = 0

            query.update(valor=valor_entregable)


        return None

    def get_novedades_ruta_estrategia_retoma(self):

        q = Q(estado = 'Nuevo') | Q(estado = 'Actualizado')

        retomas = Retoma.objects.filter(ruta = self).filter(q).aggregate(Sum('bolsas'))['bolsas__sum']

        return retomas if retomas != None else 0

    def get_novedades_sede_ruta(self, entregable_ruta):
        from cpe_2018 import forms
        self.modelos = {
            'evento_municipal': {
                'modelo': EventoMunicipal,
                'registro': RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': EventoInstitucional,
                'registro': RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': ActaPostulacion,
                'registro': RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': BaseDatosPostulante,
                'registro': RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': ActualizacionDirectorioSedes,
                'registro': RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': ActualizacionDirectorioMunicipios,
                'registro': RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': CronogramaTalleres,
                'registro': RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': DocumentoLegalizacion,
                'registro': RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': RelatoriaGraduacionDocentes,
                'registro': RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            },
            'documento_legalizacion_terminales': {
                'modelo': DocumentoLegalizacionTerminales,
                'registro': RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': DocumentoLegalizacionTerminalesValle1,
                'registro': RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': DocumentoLegalizacionTerminalesValle2,
                'registro': RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': RelatoriaTallerApertura,
                'registro': RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': CuenticosTallerApertura,
                'registro': RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': RelatoriaTallerAdministratic,
                'registro': RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': InfoticTallerAdministratic,
                'registro': RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': RelatoriaTallerContenidosEducativos,
                'registro': RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': DibuarteTallerContenidosEducativos,
                'registro': RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': RelatoriaTallerRAEE,
                'registro': RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': EcoraeeTallerRAEE,
                'registro': RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            }
        }

        object = None

        if entregable_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(entregable_ruta.entregable.modelo)['modelo']
            if modelo != None:
                try:
                    object = modelo.objects.get(ruta = self)
                except:
                    pass

            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")



        novedad = 0

        if object != None:
            if object.estado == 'Actualizado' or object.estado == 'Nuevo':
                novedad = 1

        return novedad

    def get_novedades_sede(self, entregable_ruta, radicado):


        if entregable_ruta.entregable.modelo == 'documento_legalizacion_terminales':
            try:
                object = DocumentoLegalizacionTerminales.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'documento_legalizacion_terminales_v1':
            try:
                object = DocumentoLegalizacionTerminalesValle1.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'documento_legalizacion_terminales_v2':
            try:
                object = DocumentoLegalizacionTerminalesValle2.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'relatoria_taller_apertura':
            try:
                object = RelatoriaTallerApertura.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'cuenticos_taller_apertura':
            try:
                object = CuenticosTallerApertura.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'registro_fotografico_taller_apertura':
            try:
                object = RegistroFotograficoTallerApertura.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'relatoria_taller_administratic':
            try:
                object = RelatoriaTallerAdministratic.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'infotic_taller_administratic':
            try:
                object = InfoticTallerAdministratic.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'registro_fotografico_taller_administratic':
            try:
                object = RegistroFotograficoTallerAdministratic.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'relatoria_taller_contenidos_educativos':
            try:
                object = RelatoriaTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'dibuarte_taller_contenidos_educativos':
            try:
                object = DibuarteTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'registro_fotografico_taller_contenidos_educativos':
            try:
                object = RegistroFotograficoTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'relatoria_taller_raee':
            try:
                object = RelatoriaTallerRAEE.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'ecoraee_taller_raee':
            try:
                object = EcoraeeTallerRAEE.objects.get(ruta=self,radicado = radicado)
            except:
                object = None


        elif entregable_ruta.entregable.modelo == 'registro_fotografico_taller_raee':
            try:
                object = RegistroFotograficoTallerRAEE.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        elif entregable_ruta.entregable.modelo == 'encuesta_monitoreo':
            try:
                object = EncuestaMonitoreo.objects.get(ruta=self,radicado = radicado)
            except:
                object = None

        else:
            raise NotImplementedError("EL modelo no esta establecido")


        novedad = 0

        if object != None:
            if object.estado == 'Actualizado' or object.estado == 'Nuevo':
                novedad = 1

        return novedad

    def get_novedades_sede_radicado(self, id_radicado):

        novedad = 0
        radicado = Radicados.objects.get(id = id_radicado)

        for entregable in Entregables.objects.filter(tipo='sede'):

            if entregable.modelo == 'documento_legalizacion_terminales':
                try:
                    object = DocumentoLegalizacionTerminales.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'documento_legalizacion_terminales_v1':
                try:
                    object = DocumentoLegalizacionTerminalesValle1.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'documento_legalizacion_terminales_v2':
                try:
                    object = DocumentoLegalizacionTerminalesValle2.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'relatoria_taller_apertura':
                try:
                    object = RelatoriaTallerApertura.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'cuenticos_taller_apertura':
                try:
                    object = CuenticosTallerApertura.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'registro_fotografico_taller_apertura':
                try:
                    object = RegistroFotograficoTallerApertura.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'relatoria_taller_administratic':
                try:
                    object = RelatoriaTallerAdministratic.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'infotic_taller_administratic':
                try:
                    object = InfoticTallerAdministratic.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'registro_fotografico_taller_administratic':
                try:
                    object = RegistroFotograficoTallerAdministratic.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'relatoria_taller_contenidos_educativos':
                try:
                    object = RelatoriaTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'dibuarte_taller_contenidos_educativos':
                try:
                    object = DibuarteTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'registro_fotografico_taller_contenidos_educativos':
                try:
                    object = RegistroFotograficoTallerContenidosEducativos.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'relatoria_taller_raee':
                try:
                    object = RelatoriaTallerRAEE.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'ecoraee_taller_raee':
                try:
                    object = EcoraeeTallerRAEE.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None


            elif entregable.modelo == 'registro_fotografico_taller_raee':
                try:
                    object = RegistroFotograficoTallerRAEE.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            elif entregable.modelo == 'encuesta_monitoreo':
                try:
                    object = EncuestaMonitoreo.objects.get(ruta=self,radicado = radicado)
                except:
                    object = None

            else:
                raise NotImplementedError("EL modelo no esta establecido")



            if object != None:
                if object.estado == 'Actualizado' or object.estado == 'Nuevo':
                    novedad += 1

        return novedad

    def get_novedades_componente(self, componente):

        novedades = 0
        q = Q(estado = 'Actualizado') | Q(estado = 'Nuevo')

        for entregable in Entregables.objects.filter(momento__estrategia__componente__id = componente.id):

            if componente.numero == 1:

                if entregable.modelo == 'evento_municipal':
                    novedades += EventoMunicipal.objects.filter(ruta = self).filter(q).count()
                elif entregable.modelo == 'evento_institucional':
                    novedades += EventoInstitucional.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'acta_postulacion':
                    novedades += ActaPostulacion.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'base_datos_postulante':
                    novedades += BaseDatosPostulante.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'actualizacion_directorio_sedes':
                    novedades += ActualizacionDirectorioSedes.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'actualizacion_directorio_municipios':
                    novedades += ActualizacionDirectorioMunicipios.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'cronograma_talleres':
                    novedades += CronogramaTalleres.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'documento_legalizacion':
                    novedades += DocumentoLegalizacion.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'relatoria_graduacion_docentes':
                    novedades += RelatoriaGraduacionDocentes.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'retoma':
                    novedades += self.get_novedades_ruta_estrategia_retoma()
                elif entregable.modelo == 'talleres_fomento_uso':
                    pass
                elif entregable.modelo == 'documento_legalizacion_terminales':
                    novedades += DocumentoLegalizacionTerminales.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'documento_legalizacion_terminales_v1':
                    novedades += DocumentoLegalizacionTerminalesValle1.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'documento_legalizacion_terminales_v2':
                    novedades += DocumentoLegalizacionTerminalesValle2.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'relatoria_taller_apertura':
                    novedades += RelatoriaTallerApertura.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'cuenticos_taller_apertura':
                    novedades += CuenticosTallerApertura.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'registro_fotografico_taller_apertura':
                    novedades += RegistroFotograficoTallerApertura.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'relatoria_taller_administratic':
                    novedades += RelatoriaTallerAdministratic.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'infotic_taller_administratic':
                    novedades += InfoticTallerAdministratic.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'registro_fotografico_taller_administratic':
                    novedades += RegistroFotograficoTallerAdministratic.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'relatoria_taller_contenidos_educativos':
                    novedades += RelatoriaTallerContenidosEducativos.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'dibuarte_taller_contenidos_educativos':
                    novedades += DibuarteTallerContenidosEducativos.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'registro_fotografico_taller_contenidos_educativos':
                    novedades += RegistroFotograficoTallerContenidosEducativos.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'relatoria_taller_raee':
                    novedades += RelatoriaTallerRAEE.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'ecoraee_taller_raee':
                    novedades += EcoraeeTallerRAEE.objects.filter(ruta=self).filter(q).count()
                elif entregable.modelo == 'registro_fotografico_taller_raee':
                    novedades += RegistroFotograficoTallerRAEE.objects.filter(ruta=self).filter(q).count()






                else:
                    pass

            elif componente.numero == 2:
                pass
            elif componente.numero == 3:
                pass

        if componente.numero == 2:
            novedades = 0
            for grupo in Grupos.objects.filter(ruta = self):
                novedades += grupo.get_novedades()

        return novedades

    def get_novedades_ruta(self):

        novedad = 0

        for componente in Componentes.objects.all():
            novedad += self.get_novedades_componente(componente)

        return novedad

    def get_name_entregable(self, id):
        name = ''

        try:
            name = Entregables.objects.get(id = id).momento.nombre
        except:
            try:
                name = Componentes.objects.get(id = id).nombre
            except:
                pass

        return name

    def pretty_print_valor(self):
        return str(self.contrato.valor).replace('COL','')

    def valor_ruta_entregable_estrategia(self,entregable):
        query = EntregableRutaObject.objects.filter(entregable = entregable, padre = 'ruta&estrategia&{0}'.format(self.id))
        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0


    def valor_ruta_entregable_estrategia_corte(self,entregable,corte):
        query = EntregableRutaObject.objects.filter(entregable = entregable, padre = 'ruta&estrategia&{0}'.format(self.id), corte = corte)
        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0


    def progreso_ruta_entregable_estrategia(self,entregable):
        query_total = EntregableRutaObject.objects.filter(entregable = entregable, padre = 'ruta&estrategia&{0}'.format(self.id))
        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')
        progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )


    def get_valor_ejecutado(self):
        valor = EntregableRutaObject.objects.filter(ruta = self,para_pago = True, estado__in = ["Pagado","Reportado"]).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '$ {:20,.2f}'.format(valor)




    def progreso_ruta_entregable_radicado(self,entregable, radicado):
        query_total = EntregableRutaObject.objects.filter(ruta = self,entregable = entregable, padre = 'sede&{0}'.format(radicado.id))
        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')
        progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def progreso_ruta_radicado(self,entregable, radicado):
        query_total = EntregableRutaObject.objects.filter(ruta = self, padre = 'sede&{0}'.format(radicado.id))
        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')
        progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def progreso_sede_ruta_entregable(self,entregable):
        query_total = EntregableRutaObject.objects.filter(entregable = entregable, padre = 'sede&ruta&{0}'.format(self.id))
        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')
        progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def progreso_sede_ruta_si_formacion_entregable(self,entregable):
        query_total = EntregableRutaObject.objects.filter(entregable = entregable, padre = 'sede&ruta&siformacion&{0}'.format(self.id))
        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')
        progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def progreso_ruta_componente(self,componente):

        if componente.numero == 1:
            q = Q(padre='sede&ruta&siformacion&{0}'.format(self.id)) | Q(padre='sede&ruta&{0}'.format(self.id)) | \
                Q(padre="ruta&estrategia&{0}".format(self.id)) | Q(entregable__tipo = "sede",ruta = self)
            query_total = EntregableRutaObject.objects.filter(q).filter(para_pago = True)
        elif componente.numero == 2:

            q_total = []

            for grupo in Grupos.objects.filter(ruta = self):
                q = EntregableRutaObject.objects.filter(Q(padre='docente&{0}&{1}'.format(self.id,grupo.id))).filter(para_pago = True)
                q_total += list(q.values_list('id',flat=True))

            query_total = EntregableRutaObject.objects.filter(id__in = q_total)

        elif componente.numero == 3:
            query_total = EntregableRutaObject.objects.none()
        else:
            query_total = EntregableRutaObject.objects.none()

        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')


        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0

        valor_total = self.get_valor_componente(componente)

        if valor_total != 0:
            progreso = ((valor_reportado + valor_pagado) * 100) / valor_total
        else:
            progreso = 0

        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))



        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )


    def get_valor_liquidacion(self):
        entregables = EntregableRutaObject.objects.filter(ruta = self,estado = "Reportado",corte = None,para_pago = True)

        valor = 0

        if entregables.aggregate(Sum('valor'))['valor__sum'] != None:
            valor = entregables.aggregate(Sum('valor'))['valor__sum']

        return valor


    def progreso_ruta(self):

        q_total = []

        for grupo in Grupos.objects.filter(ruta = self):
            q = EntregableRutaObject.objects.filter(Q(padre='docente&{0}&{1}'.format(self.id,grupo.id)))
            q_total += list(q.values_list('id',flat=True))



        q = Q(padre='sede&ruta&siformacion&{0}'.format(self.id)) | Q(padre='sede&ruta&{0}'.format(self.id)) | \
            Q(padre="ruta&estrategia&{0}".format(self.id)) | Q(entregable__tipo="sede", ruta=self)

        q_total += list(EntregableRutaObject.objects.filter(q).values_list('id',flat=True))

        query_total = EntregableRutaObject.objects.filter(id__in=q_total,para_pago = True)

        query_reportado = query_total.filter(estado = 'Reportado')
        query_pagado = query_total.filter(estado='Pagado')


        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0

        valor_total = self.contrato.valor.amount

        if valor_total != 0:
            progreso = ((valor_reportado + valor_pagado) * 100) / valor_total
        else:
            progreso = 0

        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))



        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )



    def progreso_ruta_actividades(self):

        modelos_acceso = self.get_modelos_ruta_acceso()
        modelos_formacion = self.get_modelos_ruta_formacion()

        query_total = EntregableRutaObject.objects.filter(ruta = self).exclude(entregable = None).exclude(valor = 0)

        query_aprobados = query_total.filter(estado__in = ['Pagado','Reportado'])

        nuevos_acceso = 0
        nuevos_formacion = 0

        for key in modelos_acceso.keys():
            modelo = modelos_acceso[key]['modelo']

            if key == 'retoma':
                bolsas = modelo.objects.filter(ruta = self, estado = 'Nuevo').aggregate(Sum('bolsas'))['bolsas__sum']
                if bolsas == None:
                    bolsas = 0
                nuevos_acceso += bolsas
            else:
                nuevos_acceso += modelo.objects.filter(ruta=self, estado='Nuevo').count()


        for key in modelos_formacion.keys():
            modelo = modelos_formacion[key]['modelo']
            nuevos_formacion += modelo.objects.filter(grupo__ruta=self, estado='Nuevo').values_list('docentes',flat = True).count()

        total = query_aprobados.count() + nuevos_acceso + nuevos_formacion

        return ('{:20,.2f}%'.format((total/query_total.count())*100.0), nuevos_acceso, nuevos_formacion)



    def pretty_print_actividades(self):
        response = ''

        actividades = json.loads(self.actividades_json)

        for actividad in actividades:
            response += '<p style="font-size:0.7rem;"><b>{0}: </b>{1}</p>'.format(
                self.get_name_entregable(actividad),
                actividades[actividad]
            )

        response += '<p style="font-size:0.7rem;"><b>{0}: </b>{1}</p>'.format(
            'Radicados',
            Radicados.objects.filter(ruta = self).count()
        )

        return response

    def get_valor_componente(self, componente):

        valor = 0

        if componente.numero == 1:
            #radicados_ids = []

            #for id in Radicados.objects.filter(ruta=self).values_list('id', flat=True):
            #    radicados_ids.append('sede&{0}'.format(id))

            q = Q(padre='sede&ruta&siformacion&{0}'.format(self.id)) | \
                Q(padre='sede&ruta&{0}'.format(self.id)) | \
                Q(tipo='Radicado') | Q(padre='ruta&estrategia&{0}'.format(self.id))

            query = EntregableRutaObject.objects.filter(ruta=self).filter(q)

            valor = query.aggregate(Sum('valor'))['valor__sum']


        elif componente.numero == 2:

            q = Q(ruta = self, tipo = "Docente")

            query = EntregableRutaObject.objects.filter(q)

            valor = query.aggregate(Sum('valor'))['valor__sum']

        elif componente.numero == 3:

            q = Q(padre='servicio&{0}'.format(self.id))

            query = EntregableRutaObject.objects.filter(q)

            valor = query.aggregate(Sum('valor'))['valor__sum']

        return valor if valor != None else 0

    def get_valor_componente_corte(self, componente, corte):

        valor = 0

        if componente.numero == 1:
            radicados_ids = []

            for id in Radicados.objects.filter(ruta=self).values_list('id', flat=True):
                radicados_ids.append('sede&{0}'.format(id))

            q = Q(padre='sede&ruta&siformacion&{0}'.format(self.id)) | \
                Q(padre='sede&ruta&{0}'.format(self.id)) | \
                Q(padre__in=radicados_ids) | Q(padre='ruta&estrategia&{0}'.format(self.id))

            if corte != None:
                query = EntregableRutaObject.objects.filter(q).filter(corte = corte)
            else:
                query = EntregableRutaObject.objects.filter(q).exclude(liquidacion = None)

            valor = query.aggregate(Sum('valor'))['valor__sum']


        elif componente.numero == 2:

            q = Q(ruta = self, tipo = "Docente")

            if corte != None:
                query = EntregableRutaObject.objects.filter(q).filter(corte = corte)
            else:
                query = EntregableRutaObject.objects.filter(q).exclude(liquidacion = None)

            valor = query.aggregate(Sum('valor'))['valor__sum']

        elif componente.numero == 3:

            q = Q(padre='servicio&{0}'.format(self.id))

            if corte != None:
                query = EntregableRutaObject.objects.filter(q).filter(corte = corte)
            else:
                query = EntregableRutaObject.objects.filter(q).exclude(liquidacion = None)

            valor = query.aggregate(Sum('valor'))['valor__sum']

        return valor if valor != None else 0

    def set_objetos_ruta_estrategia(self, retoma):
        objetos = EntregableRutaObject.objects.filter(ruta=self, estado='asignado', padre="ruta&estrategia&{0}".format(self.id))

        if objetos.count() >= retoma.bolsas:
            ids = objetos[0:retoma.bolsas].values_list('id',flat=True)
            EntregableRutaObject.objects.filter(id__in = ids).update(estado = 'Reportado', soporte = "retoma&{0}".format(retoma.id))
        else:
            raise ValueError(
                    'La cantidad de bolsas aprobadas en la retoma es superior a la dispuesta en el ruteo.'
                )

        return None

    def get_valor_ruta_estrategia_id(self,id):
        query = EntregableRutaObject.objects.filter(soporte='retoma&{0}'.format(id))
        valor = query.aggregate(Sum('valor'))['valor__sum']
        valor = valor if valor != None else 0
        return '$ {:20,.2f}'.format(float(valor))

    def get_valor_corte(self):
        objetos = EntregableRutaObject.objects.filter(estado = "Reportado", ruta = self)
        valor = objetos.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_modelos_ruta_acceso(self):
        modelos = {
            'retoma': {
                'modelo': Retoma,
                'registro': RegistroRetoma
            },
            'cuenticos_taller_apertura': {
                'modelo': CuenticosTallerApertura,
                'registro': RegistroCuenticosTallerApertura
            },
            'infotic_taller_administratic': {
                'modelo': InfoticTallerAdministratic,
                'registro': RegistroInfoticTallerAdministratic
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': DibuarteTallerContenidosEducativos,
                'registro': RegistroDibuarteTallerContenidosEducativos
            },
            'ecoraee_taller_raee': {
                'modelo': EcoraeeTallerRAEE,
                'registro': RegistroEcoraeeTallerRAEE
            },
            'documento_legalizacion_terminales': {
                'modelo': DocumentoLegalizacionTerminales,
                'registro': RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': DocumentoLegalizacionTerminalesValle1,
                'registro': RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': DocumentoLegalizacionTerminalesValle2,
                'registro': RegistroDocumentoLegalizacionTerminalesValle2
            },
            'evento_municipal': {
                'modelo': EventoMunicipal,
                'registro': RegistroEventoMunicipal
            },
            'evento_institucional': {
                'modelo': EventoInstitucional,
                'registro': RegistroEventoInstitucional
            },
            'acta_postulacion': {
                'modelo': ActaPostulacion,
                'registro': RegistroActaPostulacion
            },
            'base_datos_postulante': {
                'modelo': BaseDatosPostulante,
                'registro': RegistroBaseDatosPostulante
            },
            'actualizacion_directorio_sedes': {
                'modelo': ActualizacionDirectorioSedes,
                'registro': RegistroActualizacionDirectorioSedes
            },
            'actualizacion_directorio_municipios': {
                'modelo': ActualizacionDirectorioMunicipios,
                'registro': RegistroActualizacionDirectorioMunicipios
            },
            'cronograma_talleres': {
                'modelo': CronogramaTalleres,
                'registro': RegistroCronogramaTalleres
            },
            'documento_legalizacion': {
                'modelo': DocumentoLegalizacion,
                'registro': RegistroDocumentoLegalizacion
            },
            'relatoria_graduacion_docentes': {
                'modelo': RelatoriaGraduacionDocentes,
                'registro': RegistroRelatoriaGraduacionDocentes
            },
            'relatoria_taller_apertura': {
                'modelo': RelatoriaTallerApertura,
                'registro': RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': RelatoriaTallerAdministratic,
                'registro': RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': RelatoriaTallerContenidosEducativos,
                'registro': RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': RelatoriaTallerRAEE,
                'registro': RegistroRelatoriaTallerRAEE
            },
            'encuesta_monitoreo': {
                'modelo': EncuestaMonitoreo,
                'registro': RegistroEncuestaMonitoreo
            }
        }
        return modelos

    def get_modelos_ruta_formacion(self):
        modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': DocumentoCompromisoInscripcion,
                'registro': RegistroDocumentoCompromisoInscripcion
            },
            'instrumento_autoreporte': {
                'modelo': InstrumentoAutoreporte,
                'registro': RegistroInstrumentoAutoreporte
            },
            'instrumento_evaluacion': {
                'modelo': InstrumentoEvaluacion,
                'registro': RegistroInstrumentoEvaluacion
            },
            'acta_posesion_docente': {
                'modelo': ActaPosesionDocente,
                'registro': RegistroActaPosesionDocente
            },
            'base_datos_docentes': {
                'modelo': BaseDatosDocentes,
                'registro': RegistroBaseDatosDocentes
            },
            'documento_proyeccion_cronograma': {
                'modelo': DocumentoProyeccionCronograma,
                'registro': RegistroDocumentoProyeccionCronograma
            },
            'listado_asistencia': {
                'modelo': ListadoAsistencia,
                'registro': RegistroListadoAsistencia
            },
            'instrumento_estructuracion_ple': {
                'modelo': InstrumentoEstructuracionPle,
                'registro': RegistroInstrumentoEstructuracionPle
            },
            'producto_final_ple': {
                'modelo': ProductoFinalPle,
                'registro': RegistroProductoFinalPle
            },
            'presentacion_apa': {
                'modelo': PresentacionApa,
                'registro': RegistroPresentacionApa
            },
            'instrumento_hagamos_memoria': {
                'modelo': InstrumentoHagamosMemoria,
                'registro': RegistroInstrumentoHagamosMemoria
            },
            'presentacion_actividad_pedagogica': {
                'modelo': PresentacionActividadPedagogica,
                'registro': RegistroPresentacionActividadPedagogica
            },
            'repositorio_actividades': {
                'modelo': RepositorioActividades,
                'registro': RegistroRepositorioActividades
            },
            'sistematizacion_experiencia': {
                'modelo': SistematizacionExperiencia,
                'registro': RegistroSistematizacionExperiencia
            }
        }
        return modelos

class Radicados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    municipio = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING)

    numero = models.IntegerField(unique=True)
    nombre_ie = models.CharField(max_length=200)
    dane_sede = models.CharField(max_length=100)
    nombre_sede = models.CharField(max_length=200)
    tipologia_sede = models.CharField(max_length=10)
    ubicacion = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)

    portatiles = models.IntegerField(blank=True,null=True)
    kvd = models.IntegerField(blank=True,null=True)
    equipos_escritorio = models.IntegerField(blank=True,null=True)
    tabletas = models.IntegerField(blank=True,null=True)
    matricula = models.IntegerField(blank=True,null=True)
    observaciones = models.CharField(max_length=1000,blank=True,null=True)

    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,blank=True,null=True)

    def objetos_radicado(self, ruta, valor):

        for entregable in Entregables.objects.filter(tipo = 'sede'):

            query = EntregableRutaObject.objects.filter(
                entregable = entregable,
                padre = 'sede&{0}'.format(self.id)
            )

            if query.count() == 0:
                EntregableRutaObject.objects.create(
                    entregable = entregable,
                    ruta = ruta,
                    valor = valor,
                    estado = 'asignado',
                    padre = 'sede&{0}'.format(self.id),
                    orden = entregable.orden,
                    tipo = 'Radicado',
                    radicado = self
                )
            else:

                if query.count() == query.filter(estado__in = ['Cerrado','Pagado','Reportado']).count():

                    if query.filter(estado__in=['Pagado','Reportado']).count() > 0:
                        pass
                    else:
                        EntregableRutaObject.objects.create(
                            entregable=entregable,
                            ruta=ruta,
                            valor=valor,
                            estado='asignado',
                            padre='sede&{0}'.format(self.id),
                            orden=entregable.orden,
                            tipo='Radicado',
                            radicado=self
                        )

                else:
                    raise ValueError(
                        'No debe existir mas de un objeto para el entregable {0} del radicado {1}'.format(
                            entregable.id,
                            self.id
                        )
                    )


        return None

    def get_valor_radicado_ruta(self, ruta):
        valor = 0

        for actividad in ActividadesRadicados.objects.filter(radicado = self):
            valor += actividad.valor

        return valor

    def get_contratista(self):

        contratista = ''

        if self.ruta != None and self.ruta != '':
            if self.ruta.contratista != None and self.ruta.contratista != '':
                contratista = self.ruta.contratista.get_full_name()

        return contratista

    def get_ruta(self):

        ruta = ''

        if self.ruta != None and self.ruta != '':
            ruta = self.ruta.nombre

        return ruta

    def create_actividad(self, actividad, ruta, valor, estado, usuario):
        response = ''

        try:
            actividad = ActividadesRadicados.objects.get(actividad=actividad,radicado = self)
        except:
            actividad = ActividadesRadicados.objects.create(
                actividad = actividad,
                numero = actividad.numero,
                radicado = self,
                ruta = ruta,
                valor = valor,
                estado = estado
            )

            if ruta.contratista != None:
                observacion = 'Actividad creada, asignada a la ruta {0} del contratista {1}, C.C. {2} - Valor: {3}'.format(
                    ruta.nombre,
                    ruta.contratista.get_full_name(),
                    str(ruta.contratista.cedula),
                    '$ {:,.2f}'.format(valor)
                )
            else:
                observacion = 'Actividad creada, asignada a la ruta {0} - Valor: {1}'.format(ruta.nombre,'$ {:,.2f}'.format(valor))

                TrazabilidadActividadesRadicados.objects.create(
                actividad = actividad,
                usuario_creacion = usuario,
                observacion = observacion
            )

            response = 'Asignada'
        else:
            if actividad.estado == 'Asignada' or actividad.estado == 'Pagada' or actividad.estado == 'ANDES':
                response = actividad.estado

            elif actividad.estado == 'Disponible':

                actividad.ruta = ruta
                actividad.valor = valor
                actividad.estado = 'Asignada'
                actividad.save()


                if ruta.contratista != None:
                    observacion = 'Actividad actualizada, asignada a la ruta {0} del contratista {1}, C.C. {2} - Valor: {3}'.format(
                        ruta.nombre,
                        ruta.contratista.get_full_name(),
                        str(ruta.contratista.cedula),
                        '$ {:,.2f}'.format(valor)
                    )
                else:
                    observacion = 'Actividad actualizada, asignada a la ruta {0} - Valor: {1}'.format(
                        ruta.nombre,
                        '$ {:,.2f}'.format(valor)
                    )

                    TrazabilidadActividadesRadicados.objects.create(
                    actividad=actividad,
                    usuario_creacion=usuario,
                    observacion = observacion
                )

                response = 'Asignada'

        return response

    def __str__(self):
        return '{0} - {1}, {2}'.format(str(self.numero),self.municipio.nombre, self.municipio.departamento.nombre)

    def get_list_legalizacion(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = DocumentoLegalizacionTerminales.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista

    def get_list_encuesta(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = EncuestaMonitoreo.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista

    def get_list_taller_apertura(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = RelatoriaTallerApertura.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]


        return lista

    def get_list_taller_administratic(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = RelatoriaTallerAdministratic.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]


        return lista

    def get_list_taller_contenidos(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = RelatoriaTallerContenidosEducativos.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]


        return lista

    def get_list_taller_raee(self):
        lista = ['','FFFFFFFF','FF000000']

        objetos = RelatoriaTallerRAEE.objects.filter(radicado = self)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']
            else:
                lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF', 'Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF', 'Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista





    def get_estado_legalizacion(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = DocumentoLegalizacionTerminales.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]

    def get_estado_encuesta(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = EncuestaMonitoreo.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]

    def get_estado_taller_apertura(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = RelatoriaTallerApertura.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]

    def get_estado_taller_administratic(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = RelatoriaTallerAdministratic.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]

    def get_estado_taller_contenidos(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = RelatoriaTallerContenidosEducativos.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]

    def get_estado_taller_raee(self):
        lista = ['', 'FFFFFFFF', 'FF000000']

        objetos = RelatoriaTallerRAEE.objects.filter(radicado=self)
        rechazos = objetos.filter(estado='Rechazado')

        if rechazos.count() > 0:
            if rechazos[0].red == None:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']
            else:
                lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazado: Red {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado='Aprobado')
        except:
            try:
                nuevo = objetos.get(estado='Nuevo')
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Nuevo', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: Red {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['Aprobado', 'FF00b050', 'FFFFFFFF','Aprobado: Red {0}'.format(aprobado.red.consecutivo)]

        return lista[0]





    def get_progreso(self):

        estados = [
            self.get_estado_legalizacion(),
            self.get_estado_encuesta(),
            self.get_estado_taller_apertura(),
            self.get_estado_taller_administratic(),
            self.get_estado_taller_contenidos(),
            self.get_estado_taller_raee()
        ]


        progreso = (100.0 * estados.count('Aprobado')) / 6



        return '{:20,.2f}%'.format(progreso)


def upload_dinamic_dir_file(instance, filename):
    return '/'.join(['Acceso - CPE', 'Bd', str(instance.id), filename])

class ActualizacionRadicados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_db_acceso", on_delete=models.DO_NOTHING)

    file = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True)
    result = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True,storage=fs)
    modificados = models.IntegerField(default=0)
    nuevos = models.IntegerField(default=0)
    rechazados = models.IntegerField(default=0)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_result(self):
        url = None
        try:
            url = self.result.url
        except:
            pass
        return url

class ActualizacionDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_db_acceso_docentes", on_delete=models.DO_NOTHING)

    file = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True)
    result = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True,storage=fs)
    modificados = models.IntegerField(default=0)
    nuevos = models.IntegerField(default=0)
    rechazados = models.IntegerField(default=0)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_result(self):
        url = None
        try:
            url = self.result.url
        except:
            pass
        return url

class TrazabilidadRadicados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    radicado = models.ForeignKey(Radicados, related_name="trazabilidad_radicado", on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_trazabilidad", on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=200)


    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def __str__(self):
        return str(self.radicado.numero)

class TrazabilidadRutas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, related_name="trazabilidad_rutas", on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_trazabilidad_rutas", on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=200)

    def __str__(self):
        return self.ruta.nombre


    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

class Componentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField()
    cantidad = models.IntegerField(default=0)
    tipo = models.CharField(max_length=100)
    modelo = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Estrategias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    componente = models.ForeignKey(Componentes, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField()
    cantidad = models.IntegerField(default=0)
    tipo = models.CharField(max_length=100)
    modelo = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    def get_consecutivo(self):
        return '{0}.{1}'.format(self.componente.numero,self.numero)


    def get_cantidad_novedades_red(self, red):

        cantidad = 0

        if self.nombre == 'InnovaTIC':

            asistencias_innovatic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',estado__in=["Nuevo", "Actualizado"])
            ple_innovatic = ProductoFinalPle.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',estado__in=["Nuevo", "Actualizado"])
            cantidad = asistencias_innovatic.count() + ple_innovatic.count()

        elif self.nombre == 'RuralTIC':

            asistencias_ruraltic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',estado__in=["Nuevo", "Actualizado"])
            repositorio_ruraltic = RepositorioActividades.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',estado__in=["Nuevo", "Actualizado"])
            cantidad = asistencias_ruraltic.count() + repositorio_ruraltic.count()

        else:
            pass

        return cantidad

    def get_cantidad_red(self, red):

        cantidad = 0

        if self.nombre == 'InnovaTIC':

            asistencias_innovatic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC')
            ple_innovatic = ProductoFinalPle.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC')
            cantidad = asistencias_innovatic.count() + ple_innovatic.count()

        elif self.nombre == 'RuralTIC':

            asistencias_ruraltic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC')
            repositorio_ruraltic = RepositorioActividades.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC')
            cantidad = asistencias_ruraltic.count() + repositorio_ruraltic.count()

        else:
            pass

        return cantidad

class Grupos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_grupo", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_grupo",on_delete=models.DO_NOTHING,blank=True, null=True)

    estrategia = models.ForeignKey(Estrategias, on_delete=models.DO_NOTHING)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    numero = models.IntegerField()

    def __str__(self):
        return '{0}-{1}'.format(self.ruta.nombre,self.numero)


    def get_traslado(self):
        traslado = "No"

        docentes_ruta_ids = list(EntregableRutaObject.objects.filter(ruta = self.ruta).exclude(docente = None).values_list('docente__id',flat = True).distinct())
        docentes_otras_ruta_ids = list(EntregableRutaObject.objects.filter(docente__in = docentes_ruta_ids).exclude(docente = None,ruta = self.ruta).values_list('docente__id',flat = True))

        resultado = list(set(docentes_ruta_ids) & set(docentes_otras_ruta_ids))
        #resultado = [x for x in docentes_ruta_ids if x in docentes_otras_ruta_ids]

        if len(resultado) > 0:
            traslado = "Si"

        return traslado


    def transladar_grupo(self,ruta_destino):


        EntregableRutaObject.objects.filter(
            ruta=self.ruta,
            padre='docente&{0}&{1}'.format(self.ruta.id, self.id),
        ).update(padre='docente&{0}&{1}'.format(ruta_destino.id, self.id),ruta = ruta_destino)

        self.ruta = ruta_destino
        self.save()

        return 'Ok'


    def get_cantidad_docentes(self):

        ids_docentes = EntregableRutaObject.objects.filter(ruta=self.ruta,padre='docente&{0}&{1}'.format(self.ruta.id,self.id),tipo='Docente').values_list('docente__id', flat=True)

        return Docentes.objects.filter(id__in = ids_docentes).count()

    def get_nombre_grupo(self):
        return '{0}-{1}'.format(self.ruta.nombre,self.numero)

    def get_valor_maximo(self):



        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))

        query = EntregableRutaObject.objects.filter(q)
        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_valor_corte(self,corte):



        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))

        if corte != None:
            query = EntregableRutaObject.objects.filter(q).filter(corte = corte)
        else:
            query = EntregableRutaObject.objects.filter(q).exclude(liquidacion = None)

        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_valor_maximo_entregable(self, entregable):

        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))

        query = EntregableRutaObject.objects.filter(q).filter(entregable = entregable)
        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_valor_maximo_entregable_corte(self, entregable,corte):

        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))

        if corte != None:
            query = EntregableRutaObject.objects.filter(q).filter(entregable = entregable).filter(corte = corte)
        else:
            query = EntregableRutaObject.objects.filter(q).filter(entregable = entregable).exclude(liquidacion = None)

        valor = query.aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_progreso_entregable(self,entregable):
        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))
        query_total = EntregableRutaObject.objects.filter(q).filter(entregable = entregable).exclude(valor = 0)
        query_reportado = query_total.filter(estado = 'Reportado',para_pago = True)
        query_pagado = query_total.filter(estado='Pagado',para_pago = True)

        if query_total.count() == 0:
            progreso = 0
        else:
            progreso = ((query_reportado.count() + query_pagado.count())*100)/query_total.count()

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def get_progreso(self):
        q = Q(padre='docente&{0}&{1}'.format(
            self.ruta.id,
            self.id
        ))
        query_total = EntregableRutaObject.objects.filter(q)
        query_reportado = query_total.filter(estado = 'Reportado',para_pago=True)
        query_pagado = query_total.filter(estado='Pagado')

        if query_total.count() == 0:
            progreso = 0
        else:

            query_total_valor = query_total.aggregate(Sum('valor'))['valor__sum']
            if query_total_valor == None:
                query_total_valor = 0
                progreso = 0

            else:
                query_reportado_valor = query_reportado.aggregate(Sum('valor'))['valor__sum']

                if query_reportado_valor == None:
                    query_reportado_valor = 0

                query_pagado_valor = query_pagado.aggregate(Sum('valor'))['valor__sum']

                if query_pagado_valor == None:
                    query_pagado_valor = 0

                if float(query_total_valor) == 0:
                    progreso = 0
                else:
                    progreso = ((float(query_reportado_valor) + float(query_pagado_valor))*100.0)/float(query_total_valor)

        valor_reportado = query_reportado.aggregate(Sum('valor'))['valor__sum']
        valor_reportado = valor_reportado if valor_reportado != None else 0
        valor_reportado = '$ {:20,.2f}'.format(float(valor_reportado))

        valor_pagado = query_pagado.aggregate(Sum('valor'))['valor__sum']
        valor_pagado = valor_pagado if valor_pagado != None else 0
        valor_pagado = '$ {:20,.2f}'.format(float(valor_pagado))

        return ('{:20,.2f}%'.format(progreso), valor_reportado, valor_pagado )

    def get_modelos(self):
        from cpe_2018 import forms
        modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': DocumentoCompromisoInscripcion,
                'registro': RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': InstrumentoAutoreporte,
                'registro': RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': InstrumentoEvaluacion,
                'registro': RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': ActaPosesionDocente,
                'registro': RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': BaseDatosDocentes,
                'registro': RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': DocumentoProyeccionCronograma,
                'registro': RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': ListadoAsistencia,
                'registro': RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': InstrumentoEstructuracionPle,
                'registro': RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': ProductoFinalPle,
                'registro': RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': PresentacionApa,
                'registro': RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': InstrumentoHagamosMemoria,
                'registro': RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': PresentacionActividadPedagogica,
                'registro': RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': RepositorioActividades,
                'registro': RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': SistematizacionExperiencia,
                'registro': RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }
        return modelos

    def get_novedades(self):
        novedades = 0

        modelos = self.get_modelos()

        for name in modelos.keys():
            modelo = modelos.get(name)['modelo']
            novedades += modelo.objects.filter(grupo = self, estado__in = ['Nuevo', 'Actualizado']).count()

        return novedades

class Docentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING)
    cedula = models.BigIntegerField(unique=True)
    nombre = models.CharField(max_length=500)
    estrategia = models.ForeignKey(Estrategias, on_delete=models.DO_NOTHING)
    sede = models.CharField(max_length=100,blank=True,null=True)
    telefono = models.CharField(max_length=100,blank=True,null=True)
    registro = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING, blank=True, null=True)
    actividades = models.IntegerField(blank=True,null=True)
    valor_unitario = models.IntegerField(blank=True, null=True)
    valor_total = models.IntegerField(blank=True, null=True)
    efectivo = models.BooleanField(default=False)
    producto_final_andes = models.BooleanField(default=False)
    permitir_recarga = models.BooleanField(default=False)

    def __str__(self):
        return '{0} - {1}'.format(self.cedula,self.nombre)


    def get_efectividad(self):
        efectivo = ""

        if self.efectivo:
            efectivo = "Graduado"

        return efectivo


    def progreso_actividades(self):

        modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': DocumentoCompromisoInscripcion,
                'registro': RegistroDocumentoCompromisoInscripcion
            },
            'instrumento_autoreporte': {
                'modelo': InstrumentoAutoreporte,
                'registro': RegistroInstrumentoAutoreporte
            },
            'instrumento_evaluacion': {
                'modelo': InstrumentoEvaluacion,
                'registro': RegistroInstrumentoEvaluacion
            },
            'acta_posesion_docente': {
                'modelo': ActaPosesionDocente,
                'registro': RegistroActaPosesionDocente
            },
            'base_datos_docentes': {
                'modelo': BaseDatosDocentes,
                'registro': RegistroBaseDatosDocentes
            },
            'documento_proyeccion_cronograma': {
                'modelo': DocumentoProyeccionCronograma,
                'registro': RegistroDocumentoProyeccionCronograma
            },
            'listado_asistencia': {
                'modelo': ListadoAsistencia,
                'registro': RegistroListadoAsistencia
            },
            'instrumento_estructuracion_ple': {
                'modelo': InstrumentoEstructuracionPle,
                'registro': RegistroInstrumentoEstructuracionPle
            },
            'producto_final_ple': {
                'modelo': ProductoFinalPle,
                'registro': RegistroProductoFinalPle
            },
            'presentacion_apa': {
                'modelo': PresentacionApa,
                'registro': RegistroPresentacionApa
            },
            'instrumento_hagamos_memoria': {
                'modelo': InstrumentoHagamosMemoria,
                'registro': RegistroInstrumentoHagamosMemoria
            },
            'presentacion_actividad_pedagogica': {
                'modelo': PresentacionActividadPedagogica,
                'registro': RegistroPresentacionActividadPedagogica
            },
            'repositorio_actividades': {
                'modelo': RepositorioActividades,
                'registro': RegistroRepositorioActividades
            },
            'sistematizacion_experiencia': {
                'modelo': SistematizacionExperiencia,
                'registro': RegistroSistematizacionExperiencia,
            }
        }

        entregables = Entregables.objects.filter(momento__estrategia=self.estrategia)

        aprobadas = 0

        for entregable in entregables:
            modelo = modelos[entregable.modelo]['modelo']
            objetos = modelo.objects.filter(estado = "Aprobado",entregable = entregable,docentes = self)
            if objetos.count() > 0:
                aprobadas += 1

        progreso = (100.0 * aprobadas) / entregables.count()

        return '{:20,.2f}%'.format(progreso)


    def get_nombre_grupo(self):
        nombre = ''
        if self.grupo != None:
            nombre = self.grupo.get_nombre_grupo()
        return nombre

    def verificar_objetos_formacion_estrategia(self, ruta, grupo):

        if grupo.estrategia.numero == 1:
            entregables = Entregables.objects.filter(momento__estrategia__numero = 1, tipo = 'docente')
        else:
            entregables = Entregables.objects.filter(momento__estrategia__numero = 2, tipo = 'docente')

        query = EntregableRutaObject.objects.filter(
            ruta=ruta,
            estado='asignado',
            padre='docente&{0}&{1}'.format(
                ruta.id,
                grupo.id
            ),
            tipo='Docente',
            docente=self
        )


        for entregable in entregables:
            q = query.filter(entregable = entregable)

            if q.count() > 1:
                id = q.first()
                q.exclude(id = q.first().id).delete()

        return 'Ok'

    def actualizar_objetos_formacion_estrategia(self, ruta, grupo):

        if grupo.estrategia.numero == 1:
            entregables = Entregables.objects.filter(momento__estrategia__numero = 1, tipo = 'docente')
        else:
            entregables = Entregables.objects.filter(momento__estrategia__numero = 2, tipo = 'docente')

        query = EntregableRutaObject.objects.filter(
            ruta=ruta,
            estado='asignado',
            padre='docente&{0}&{1}'.format(
                ruta.id,
                grupo.id
            ),
            tipo='Docente',
            docente=self
        )


        valor_docente = query.aggregate(Sum('valor'))['valor__sum']

        if valor_docente == None:
            valor_docente = 0





        cantidad = entregables.aggregate(Sum('peso'))['peso__sum']

        if cantidad == None:
            cantidad = 0

        if cantidad > 0:
            valor_entregable = valor_docente / cantidad
        else:
            valor_entregable = 0



        query.delete()


        for entregable in entregables:
            EntregableRutaObject.objects.create(
                entregable=entregable,
                ruta=ruta,
                valor=valor_entregable * entregable.peso,
                estado='asignado',
                padre='docente&{0}&{1}'.format(
                    self.grupo.ruta.id,
                    self.grupo.id
                ),
                tipo='Docente',
                orden=entregable.orden,
                docente=self
            )

        return 'Ok'

    def get_disabled_entregable(self,entregable):
        try:
            obj = EntregableRutaObject.objects.get(docente = self)
        except:
            obj = None
        return False if obj == None else True

    def get_disabled_entregable_form(self,entregable,estados):

        if self.permitir_recarga:
            return False

        else:

            try:
                obj = EntregableRutaObject.objects.get(docente = self, entregable = entregable,estado__in = estados)
            except:
                obj = None
            return False if obj == None else True

    def get_actividades_docentes(self, ruta, grupo):
        query = EntregableRutaObject.objects.filter(
            ruta=ruta,
            padre='docente&{0}&{1}'.format(
                ruta.id,
                grupo.id
            ),
            tipo='Docente',
            docente=self
        ).exclude(estado = 'Cerrado')
        return query.count()

    def get_valor_unitario_docentes(self, ruta, grupo):
        query = EntregableRutaObject.objects.filter(
            ruta=ruta,
            padre='docente&{0}&{1}'.format(
                ruta.id,
                grupo.id
            ),
            tipo='Docente',
            docente=self
        ).exclude(estado = 'Cerrado')
        cantidad = query.count()

        if cantidad == 0:
            valor_total = 0
            return 0
        else:
            valor_total = query.aggregate(Sum('valor'))['valor__sum']
            return valor_total/cantidad

    def get_valor_total_docentes(self, ruta, grupo):
        query = EntregableRutaObject.objects.filter(
            ruta=ruta,
            padre='docente&{0}&{1}'.format(
                ruta.id,
                grupo.id
            ),
            tipo='Docente',
            docente=self
        )
        cantidad = query.count()

        if cantidad == 0:
            return 0
        else:
            return query.aggregate(Sum('valor'))['valor__sum']

    def get_progreso(self,ruta,grupo):
        query = EntregableRutaObject.objects.filter(padre='docente&{0}&{1}'.format(ruta.id,grupo.id),tipo='Docente',docente=self)

        valor_total = query.aggregate(Sum('valor'))['valor__sum']
        if valor_total == None:
            valor_total = 0

        valor_pagado = query.filter(estado__in=['Reportado', 'Pagado']).aggregate(Sum('valor'))['valor__sum']
        if valor_pagado == None:
            valor_pagado = 0

        if valor_total == 0:
            return ('{0:.2f}%'.format(0), valor_pagado)
        else:
            return ('{0:.2f}%'.format((float(valor_pagado)/float(valor_total))*100.0),valor_pagado)

    def get_estado(self,ruta,grupo):
        estado = 'Activo'
        query = EntregableRutaObject.objects.filter(padre='docente&{0}&{1}'.format(ruta.id,grupo.id),tipo='Docente',docente=self)

        if query.filter(estado = 'Cerrado').count() > 0:
            estado = 'Retirado'

        return estado

    def get_estado_tablero_listado(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = ListadoAsistencia.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF']
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']

        return lista


    def get_estado_tablero_producto_final(self):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            objetos = ProductoFinalPle.objects.filter(docentes=self)
        elif self.estrategia.nombre == 'RuralTIC':
            objetos = RepositorioActividades.objects.filter(docentes=self)
        else:
            objetos = ProductoFinalPle.objects.none()


        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF']
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF']

        return lista

    def get_estado_tablero_producto_final_texto(self):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            objetos = ProductoFinalPle.objects.filter(docentes=self)
        elif self.estrategia.nombre == 'RuralTIC':
            objetos = RepositorioActividades.objects.filter(docentes=self)
        else:
            objetos = ProductoFinalPle.objects.none()


        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Cargado', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF']
        else:
            lista = ['Aprobado','FF00b050','FFFFFFFF']

        return lista[0]

    def get_estado_tablero_producto_final_red(self):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            objetos = ProductoFinalPle.objects.filter(docentes=self)
        elif self.estrategia.nombre == 'RuralTIC':
            objetos = RepositorioActividades.objects.filter(docentes=self)
        else:
            objetos = ProductoFinalPle.objects.none()


        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['RED {0}'.format(rechazos[0].red.consecutivo), 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['RED {0}'.format(nuevo.red.consecutivo), 'FF00b0f0', 'FFFFFFFF']
        else:
            lista = ['RED {0}'.format(aprobado.red.consecutivo),'FF00b050','FFFFFFFF']

        return lista[0]




    def get_estado_tablero_listado_texto(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = ListadoAsistencia.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['Rechazado', 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Cargado', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF']
        else:
            lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']

        return lista[0]

    def get_estado_tablero_listado_red(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = ListadoAsistencia.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['RED {0}'.format(rechazos[0].red.consecutivo), 'FFff0000', 'FFFFFFFF']

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['RED {0}'.format(nuevo.red.consecutivo), 'FF00b0f0', 'FFFFFFFF']
        else:
            if aprobado.red == None:
                lista = ['', 'FF00b050', 'FFFFFFFF']
            else:
                lista = ['RED {0}'.format(aprobado.red.consecutivo),'FF00b050','FFFFFFFF']

        return lista[0]

    def get_estado_tablero_autoreporte(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = InstrumentoAutoreporte.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazo: RED {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF','Enviado: RED {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF','Aprobado: RED {0}'.format(aprobado.red.consecutivo)]

        return lista

    def get_estado_tablero_autoreporte_texto(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = InstrumentoAutoreporte.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazo: RED {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Cargado', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: RED {0}'.format(nuevo.red.consecutivo)]
        else:
            lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']

        return lista[0]



    def get_estado_tablero_modelo_texto(self , numero_innovatic, numero_ruraltic, modelo):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
        else:
            numero = 0

        objetos = modelo.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazo: RED {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Cargado', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: RED {0}'.format(nuevo.red.consecutivo)]
        else:
            lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']

        return lista[0]



    def get_estado_tablero_evaluacion(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
            modelo = InstrumentoEvaluacion
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
            modelo = InstrumentoHagamosMemoria
        else:
            numero = 0
            modelo = None

        objetos = modelo.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = [rechazos[0].fecha.strftime('%d/%m/%Y'), 'FFff0000', 'FFFFFFFF','Rechazo: RED {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FFffc000', 'FFFFFFFF']
                else:
                    lista = [nuevo.fecha.strftime('%d/%m/%Y'), 'FF00b0f0', 'FFFFFFFF','Enviado: RED {0}'.format(nuevo.red.consecutivo)]
        else:
            if aprobado.red == None:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'), 'FF00b050', 'FFFFFFFF']
            else:
                lista = [aprobado.fecha.strftime('%d/%m/%Y'),'FF00b050','FFFFFFFF','Aprobado: RED {0}'.format(aprobado.red.consecutivo)]

        return lista

    def get_estado_tablero_evaluacion_texto(self , numero_innovatic, numero_ruraltic):
        lista = ['','FFFFFFFF','FF000000']

        if self.estrategia.nombre == 'InnovaTIC':
            numero = numero_innovatic
            modelo = InstrumentoEvaluacion
        elif self.estrategia.nombre == 'RuralTIC':
            numero = numero_ruraltic
            modelo = InstrumentoHagamosMemoria
        else:
            numero = 0
            modelo = None

        objetos = modelo.objects.filter(docentes = self,entregable__numero = numero)
        rechazos = objetos.filter(estado = 'Rechazado')

        if rechazos.count() > 0:
            lista = ['Rechazado', 'FFff0000', 'FFFFFFFF','Rechazo: RED {0}'.format(rechazos[0].red.consecutivo)]

        try:
            aprobado = objetos.get(estado = 'Aprobado')
        except:
            try:
                nuevo = objetos.get(estado__in = ['Nuevo','Actualizado'])
            except:
                pass
            else:
                if nuevo.red == None:
                    lista = ['Cargado', 'FFffc000', 'FFFFFFFF']
                else:
                    lista = ['Enviado', 'FF00b0f0', 'FFFFFFFF','Enviado: RED {0}'.format(nuevo.red.consecutivo)]
        else:
            lista = ['Aprobado', 'FF00b050', 'FFFFFFFF']

        return lista[0]

    def get_cantidad_listados_aprobados(self):
        return ListadoAsistencia.objects.filter(docentes = self,estado = "Aprobado").values_list('entregable__numero').distinct().count()



class Momentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    estrategia = models.ForeignKey(Estrategias, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField()
    cantidad = models.IntegerField(default=0)
    tipo = models.CharField(max_length=100)
    modelo = models.CharField(max_length=200)
    icon = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    def get_consecutivo(self):
        return '{0}.{1}.{2}'.format(self.estrategia.componente.numero,self.estrategia.numero,self.numero)

class Entregables(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    momento = models.ForeignKey(Momentos, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=200)
    numero = models.IntegerField()
    tipo = models.CharField(max_length=100)
    modelo = models.CharField(max_length=200)
    red = models.CharField(max_length=200)
    orden = models.IntegerField(default=0)
    peso = models.IntegerField(default=1)
    presupuesto = models.CharField(max_length=100)


    def get_cantidad_translados(self,ruta,grupo):
        translado = "No"

        ids_docentes_objetos = EntregableRutaObject.objects.filter(ruta=ruta,padre='docente&{0}&{1}'.format(ruta.id, grupo.id),tipo='Docente',entregable=self).values_list('docente__id', flat=True)
        #docentes_objetos = Docentes.objects.filter(id__in = ids_docentes_objetos)

        ids_docentes_otros_objetos = EntregableRutaObject.objects.exclude(ruta = ruta).filter(entregable=self,docente__in=ids_docentes_objetos).values_list('docente__id', flat=True)

        ids_interseccion = list(set(ids_docentes_objetos) & set(ids_docentes_otros_objetos))

        if len(ids_interseccion) > 0:
            translado = "Si"

        return translado


    def __str__(self):
        return self.nombre


    def get_estado_radicado(self,radicado,modelo):

        modelos = {
            'documento_legalizacion_terminales': DocumentoLegalizacionTerminales,
            'encuesta_monitoreo': EncuestaMonitoreo,
            'relatoria_taller_apertura': RelatoriaTallerApertura,
            'relatoria_taller_administratic': RelatoriaTallerAdministratic,
            'relatoria_taller_contenidos_educativos': RelatoriaTallerContenidosEducativos,
            'relatoria_taller_raee': RelatoriaTallerRAEE
        }

        fecha = None
        ruta = None
        lider = None
        url = None

        objetos = modelos[modelo].objects.filter(radicado__numero = radicado,estado = "Aprobado")

        if objetos.count() > 0:
            fecha = str(objetos[0].fecha)
            ruta = str(objetos[0].ruta.nombre)
            lider = '{0} - C.C.{1}'.format(objetos[0].ruta.contrato.contratista.get_full_name(),objetos[0].ruta.contrato.contratista.cedula)
            url = objetos[0].url_file()

        return [fecha,ruta,lider,url]


    def get_progreso_docente(self,cedula,modelo):

        modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': DocumentoCompromisoInscripcion,
                'registro': RegistroDocumentoCompromisoInscripcion
            },
            'instrumento_autoreporte': {
                'modelo': InstrumentoAutoreporte,
                'registro': RegistroInstrumentoAutoreporte
            },
            'instrumento_evaluacion': {
                'modelo': InstrumentoEvaluacion,
                'registro': RegistroInstrumentoEvaluacion
            },
            'acta_posesion_docente': {
                'modelo': ActaPosesionDocente,
                'registro': RegistroActaPosesionDocente
            },
            'base_datos_docentes': {
                'modelo': BaseDatosDocentes,
                'registro': RegistroBaseDatosDocentes
            },
            'documento_proyeccion_cronograma': {
                'modelo': DocumentoProyeccionCronograma,
                'registro': RegistroDocumentoProyeccionCronograma
            },
            'listado_asistencia': {
                'modelo': ListadoAsistencia,
                'registro': RegistroListadoAsistencia
            },
            'instrumento_estructuracion_ple': {
                'modelo': InstrumentoEstructuracionPle,
                'registro': RegistroInstrumentoEstructuracionPle
            },
            'producto_final_ple': {
                'modelo': ProductoFinalPle,
                'registro': RegistroProductoFinalPle
            },
            'presentacion_apa': {
                'modelo': PresentacionApa,
                'registro': RegistroPresentacionApa
            },
            'instrumento_hagamos_memoria': {
                'modelo': InstrumentoHagamosMemoria,
                'registro': RegistroInstrumentoHagamosMemoria
            },
            'presentacion_actividad_pedagogica': {
                'modelo': PresentacionActividadPedagogica,
                'registro': RegistroPresentacionActividadPedagogica
            },
            'repositorio_actividades': {
                'modelo': RepositorioActividades,
                'registro': RegistroRepositorioActividades
            },
            'sistematizacion_experiencia': {
                'modelo': SistematizacionExperiencia,
                'registro': RegistroSistematizacionExperiencia,
            }
        }

        fecha = None
        ruta = None
        lider = None
        url = None

        objetos = modelos[modelo]['modelo'].objects.filter(docentes__cedula = cedula,estado = "Aprobado",entregable=self)

        if objetos.count() > 0:
            fecha = str(objetos[0].fecha)
            ruta = str(objetos[0].grupo)
            lider = '{0} - C.C.{1}'.format(objetos[0].grupo.ruta.contrato.contratista.get_full_name(),objetos[0].grupo.ruta.contrato.contratista.cedula)
            url = objetos[0].url_file()

        return [fecha,ruta,lider,url]


    def get_cantidad_red(self, red):

        modelos = {
            'encuesta_monitoreo': {
                'modelo': EncuestaMonitoreo,
                'registro': RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': DocumentoLegalizacionTerminales,
                'registro': RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': DocumentoLegalizacionTerminalesValle1,
                'registro': RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': DocumentoLegalizacionTerminalesValle2,
                'registro': RegistroDocumentoLegalizacionTerminalesValle2
            },
            'relatoria_taller_apertura': {
                'modelo': RelatoriaTallerApertura,
                'registro': RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': RelatoriaTallerAdministratic,
                'registro': RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': RelatoriaTallerContenidosEducativos,
                'registro': RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': RelatoriaTallerRAEE,
                'registro': RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': Retoma,
                'registro': RegistroRetoma
            }
        }

        modelo = modelos[self.modelo]['modelo']

        if self.modelo == 'retoma':

            retomas = modelo.objects.filter(red = red).aggregate(Sum('bolsas'))['bolsas__sum']

            return retomas if retomas != None else 0
        else:
            return modelo.objects.filter(red=red).count()

    def get_cantidad_novedades_red(self, red):

        modelos = {
            'encuesta_monitoreo': {
                'modelo': EncuestaMonitoreo,
                'registro': RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': DocumentoLegalizacionTerminales,
                'registro': RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': DocumentoLegalizacionTerminalesValle1,
                'registro': RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': DocumentoLegalizacionTerminalesValle2,
                'registro': RegistroDocumentoLegalizacionTerminalesValle2
            },
            'relatoria_taller_apertura': {
                'modelo': RelatoriaTallerApertura,
                'registro': RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': RelatoriaTallerAdministratic,
                'registro': RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': RelatoriaTallerContenidosEducativos,
                'registro': RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': RelatoriaTallerRAEE,
                'registro': RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': Retoma,
                'registro': RegistroRetoma
            }
        }

        modelo = modelos[self.modelo]['modelo']

        return modelo.objects.filter(red=red, estado__in=["Nuevo", "Actualizado"]).count()

    def get_cantidad_formacion_red(self, red, estrategia):

        cantidad = 0

        if estrategia.nombre == 'InnovaTIC':

            asistencias_innovatic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',entregable = self)
            ple_innovatic = ProductoFinalPle.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',entregable = self)
            cantidad = asistencias_innovatic.count() + ple_innovatic.count()

        elif estrategia.nombre == 'RuralTIC':

            asistencias_ruraltic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',entregable = self)
            repositorio_ruraltic = RepositorioActividades.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',entregable = self)
            cantidad = asistencias_ruraltic.count() + repositorio_ruraltic.count()

        else:
            pass

        return cantidad

    def get_cantidad_novedades_formacion_red(self, red, estrategia):

        cantidad = 0

        if estrategia.nombre == 'InnovaTIC':

            asistencias_innovatic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',entregable = self,estado__in=["Nuevo", "Actualizado"])
            ple_innovatic = ProductoFinalPle.objects.filter(red=red, grupo__estrategia__nombre='InnovaTIC',entregable = self,estado__in=["Nuevo", "Actualizado"])
            cantidad = asistencias_innovatic.count() + ple_innovatic.count()

        elif estrategia.nombre == 'RuralTIC':

            asistencias_ruraltic = ListadoAsistencia.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',entregable = self,estado__in=["Nuevo", "Actualizado"])
            repositorio_ruraltic = RepositorioActividades.objects.filter(red=red, grupo__estrategia__nombre='RuralTIC',entregable = self,estado__in=["Nuevo", "Actualizado"])
            cantidad = asistencias_ruraltic.count() + repositorio_ruraltic.count()

        else:
            pass

        return cantidad

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}'.format(
            self.momento.estrategia.componente.numero,
            self.momento.estrategia.numero,
            self.momento.numero,
            self.numero
        )

    def get_modelos(self):
        from cpe_2018 import forms
        modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': DocumentoCompromisoInscripcion,
                'registro': RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': InstrumentoAutoreporte,
                'registro': RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': InstrumentoEvaluacion,
                'registro': RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': ActaPosesionDocente,
                'registro': RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': BaseDatosDocentes,
                'registro': RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': DocumentoProyeccionCronograma,
                'registro': RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': ListadoAsistencia,
                'registro': RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': InstrumentoEstructuracionPle,
                'registro': RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': ProductoFinalPle,
                'registro': RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': PresentacionApa,
                'registro': RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': InstrumentoHagamosMemoria,
                'registro': RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': PresentacionActividadPedagogica,
                'registro': RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': RepositorioActividades,
                'registro': RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': SistematizacionExperiencia,
                'registro': RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }
        return modelos

    def get_novedades_entregable(self,grupo,entregable):

        modelos = self.get_modelos()

        if self.modelo not in modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = modelos[self.modelo]['modelo']
            novedades = modelo.objects.filter(grupo = grupo, entregable = entregable, estado__in = ['Nuevo', 'Actualizado']).count()

        return novedades

class ActividadesRadicados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    #actividad = models.ForeignKey(Actividades, on_delete=models.DO_NOTHING)
    numero = models.IntegerField(default=0)
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP',default=0)
    estado = models.CharField(max_length=100)

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def __str__(self):
        return '{0}. {1}'.format(self.actividad.numero,self.actividad.nombre)

class TrazabilidadActividadesRadicados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    actividad = models.ForeignKey(ActividadesRadicados, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=200)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

class ActividadesRuta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    #actividad = models.ForeignKey(Actividades, on_delete=models.DO_NOTHING)
    numero = models.IntegerField(default=0)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP',default=0)
    estado = models.CharField(max_length=100)

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def __str__(self):
        return '{0}. {1}'.format(self.actividad.numero,self.actividad.nombre)

class TrazabilidadActividadesRuta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    actividad = models.ForeignKey(ActividadesRuta, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=200)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_dir_corte(instance, filename):
    return '/'.join(['Cortes', str(instance.id), filename])


class Cortes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    region = models.ForeignKey(Regiones, on_delete=models.DO_NOTHING)
    consecutivo = models.IntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    descripcion = models.CharField(max_length=200)
    file = models.FileField(upload_to=upload_dinamic_dir_corte, blank=True, null=True, storage = fs)

    def __str__(self):
        return self.descripcion


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def get_valor(self):
        valor = EntregableRutaObject.objects.filter(corte = self).aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_novedades(self):
        cuentas_cobro = CuentasCobro.objects.filter(corte = self, estado__in = ['Creado', 'Cargado'])
        return cuentas_cobro.count()

    def get_cantidad_cuentas_cobro(self):
        return CuentasCobro.objects.filter(corte = self).count()

    def create_cuentas_cobro(self, user):
        objetos = EntregableRutaObject.objects.filter(corte = self, estado = "Pagado")
        rutas_ids = objetos.values_list('ruta__id', flat=True).distinct()
        for ruta_id in rutas_ids:
            ruta = Rutas.objects.get(id = ruta_id)

            try:
                cuenta_cobro = CuentasCobro.objects.get(
                    ruta = ruta,
                    corte = self
                )
            except:

                valor = objetos.filter(ruta = ruta).aggregate(Sum('valor'))['valor__sum']

                if valor == None:
                    valor = 0

                cuenta_cobro = CuentasCobro.objects.create(
                    ruta = ruta,
                    corte = self,
                    usuario_creacion = user,
                    estado = 'Creado',
                    valor = valor
                )

            else:
                pass


        return None

    def create_excel(self):
        tasks.build_excel_corte.delay(self.id)
        return None


def upload_dinamic_cuentas_cobro(instance, filename):
    return '/'.join(['CPE 2018', 'Cuentas de Cobro', str(instance.id), filename])

class CuentasCobro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)

    fecha_actualizacion = models.DateTimeField(blank=True,null=True)
    usuario_actualizacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='usuario_actualizacion_cuentas_cobro')

    corte = models.ForeignKey(Cortes, on_delete = models.DO_NOTHING, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_cuentas_cobro,
        content_types=['application/pdf'],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_cuentas_cobro,
        content_types=['application/pdf'],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True
    )
    html = models.FileField(upload_to=upload_dinamic_cuentas_cobro, blank=True, null=True)
    delta = models.TextField(blank=True, null=True)
    data_json = models.TextField(blank=True,null=True)
    valores_json = models.TextField(default='[]',blank=True,null=True)
    observaciones = models.TextField(default='',blank=True,null=True)
    liquidacion = models.BooleanField(default=False)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def create_delta(self):
        from cpe_2018.functions import delta_cuenta_cobro
        self.delta = json.dumps(delta_cuenta_cobro(self))
        self.save()
        return None

    def get_html_delta(self):
        delta = json.loads(self.delta)
        return html.render(delta['ops'])

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_file2(self):
        url = None
        try:
            url = self.file2.url
        except:
            pass
        return url

    def pretty_print_url_file2(self):
        try:
            url = self.file2.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file2.name) +'</a>'


def upload_dinamic_liquidaciones(instance, filename):
    return '/'.join(['CPE 2018', 'Liquidaciones', str(instance.id), filename])



class Liquidaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING, blank=True, null=True)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    estado = models.CharField(max_length=100,blank=True,null = True)
    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_liquidaciones,
        content_types=['application/pdf'],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_liquidaciones,
        content_types=['application/pdf'],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_liquidaciones,
        content_types=['application/pdf'],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True,
        storage=fs
    )
    html = models.FileField(upload_to=upload_dinamic_liquidaciones, blank=True, null=True)
    delta = models.TextField(blank=True, null=True)
    data_json = models.TextField(blank=True, null=True)
    observaciones = models.TextField(default='', blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    usuario_actualizacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,related_name='usuario_actualizacion_liquidacion')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_file2(self):
        url = None
        try:
            url = self.file2.url
        except:
            pass
        return url

    def url_file3(self):
        url = None
        try:
            url = self.file3.url
        except:
            pass
        return url


class EntregableRutaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING, blank=True, null=True)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    estado = models.CharField(max_length=100)
    padre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100,default='')
    orden = models.IntegerField(default=0)
    actualizacion = models.BooleanField(default=False)
    soporte = models.CharField(max_length=100,default='')
    habilitado = models.BooleanField(default=True)
    docente = models.ForeignKey(Docentes, on_delete=models.DO_NOTHING,blank=True, null=True)
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank=True, null=True)
    corte = models.ForeignKey(Cortes, on_delete=models.DO_NOTHING, blank=True, null=True)
    liquidacion = models.ForeignKey(Liquidaciones, on_delete=models.DO_NOTHING, blank=True, null=True)
    para_pago = models.BooleanField(default=True)

    def __str__(self):
        return self.padre


    def get_radicado_numero(self):
        radicado = 'N/A'

        if self.entregable != None:

            if self.entregable.tipo == 'ruta&estrategia':
                retoma = Retoma.objects.get(id = self.soporte.split('&')[-1])
                radicado = retoma.radicado

            elif self.entregable.tipo == 'sede':
                radicado = self.radicado.numero

            else:
                pass

        return radicado


    def get_radicado_departamento(self):
        departamento = 'N/A'

        if self.entregable != None:

            if self.entregable.tipo == 'ruta&estrategia':
                retoma = Retoma.objects.get(id = self.soporte.split('&')[-1])
                departamento = retoma.municipio.departamento.nombre

            elif self.entregable.tipo == 'sede':
                departamento = self.radicado.municipio.departamento.nombre

            else:
                pass

        return departamento


    def get_radicado_municipio(self):
        municipio = 'N/A'

        if self.entregable != None:

            if self.entregable.tipo == 'ruta&estrategia':
                retoma = Retoma.objects.get(id = self.soporte.split('&')[-1])
                municipio = retoma.municipio.nombre

            elif self.entregable.tipo == 'sede':
                municipio = self.radicado.municipio.nombre

            else:
                pass

        return municipio


    def get_radicado_sede(self):
        sede = 'N/A'

        if self.entregable != None:

            if self.entregable.tipo == 'sede':
                sede = self.radicado.nombre_sede

            else:
                pass

        return sede


    def get_radicado_ubicacion(self):
        ubicacion = 'N/A'

        if self.entregable != None:

            if self.entregable.tipo == 'sede':
                ubicacion = self.radicado.ubicacion

            else:
                pass

        return ubicacion


    def get_docente_nombre(self):
        nombre = 'N/A'

        if self.tipo == 'Docente':
            try:
                nombre = self.docente.nombre
            except:
                pass

        else:
            pass

        return nombre

    def get_docente_cedula(self):
        cedula = 'N/A'

        if self.tipo == 'Docente':
            try:
                cedula = self.docente.cedula
            except:
                pass


        else:
            pass

        return cedula

    def get_docente_departamento(self):
        departamento = 'N/A'

        if self.tipo == 'Docente':
            try:
                departamento = self.docente.municipio.departamento.nombre
            except:
                pass

        else:
            pass

        return departamento

    def get_docente_municipio(self):
        municipio = 'N/A'

        if self.tipo == 'Docente':
            try:
                municipio = self.docente.municipio.nombre
            except:
                pass

        else:
            pass

        return municipio

    def get_docente_diplomado(self):
        diplomado = 'N/A'

        if self.tipo == 'Docente':
            try:
                diplomado = self.docente.estrategia.nombre
            except:
                pass

        else:
            pass

        return diplomado


    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def get_radicado(self):
        id = str(self.padre).replace('sede&','')
        return Radicados.objects.get(id = id)

    def get_radicado_valor(self,ruta):

        radicado = self.get_radicado()
        q = Q(padre='sede&{0}'.format(radicado.id))
        query = EntregableRutaObject.objects.filter(q).filter(ruta = ruta)
        valor = query.aggregate(Sum('valor'))['valor__sum']

        return valor if valor != None else 0

    def get_radicado_valor_corte(self,corte):

        radicado = self.get_radicado()
        q = Q(padre='sede&{0}'.format(radicado.id))
        query = EntregableRutaObject.objects.filter(q).filter(corte = corte)
        valor = query.aggregate(Sum('valor'))['valor__sum']

        return valor if valor != None else 0


    def get_valor_si_calificado(self):
        return str(self.valor).replace('COL','') if self.estado == 'Reportado' or self.estado == 'Pagado' else '$ {:20,.2f}'.format(0)


def upload_dinamic_red(instance, filename):
    return '/'.join(['CPE 2018', 'Reds', str(instance.id), filename])


class Red(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    region = models.ForeignKey(Regiones, on_delete=models.DO_NOTHING)
    consecutivo = models.IntegerField()
    estrategia = models.CharField(max_length=200)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_red", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_red,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True,
        storage = fs
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_red,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=5242880,
        max_length=255,
        blank=True,
        null=True,
        storage=fs
    )

    def __str__(self):
        return '{0} - {1}'.format(self.consecutivo,self.region.nombre)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_file2(self):
        url = None
        try:
            url = self.file2.url
        except:
            pass
        return url


    def generar_red(self):
        if self.estrategia == 'Acceso':
            tasks.build_red_acceso.delay(str(self.id))
        elif self.estrategia == 'Formación':
            tasks.build_red_formacion.delay(str(self.id))
        return 'Ok'

    def get_novedades_red(self):

        cantidad = 0

        if self.estrategia == "Acceso":

            modelos = {
                'encuesta_monitoreo': {
                    'modelo': EncuestaMonitoreo,
                    'registro': RegistroEncuestaMonitoreo
                },
                'documento_legalizacion_terminales': {
                    'modelo': DocumentoLegalizacionTerminales,
                    'registro': RegistroDocumentoLegalizacionTerminales
                },
                'documento_legalizacion_terminales_v1': {
                    'modelo': DocumentoLegalizacionTerminalesValle1,
                    'registro': RegistroDocumentoLegalizacionTerminalesValle1
                },
                'documento_legalizacion_terminales_v2': {
                    'modelo': DocumentoLegalizacionTerminalesValle2,
                    'registro': RegistroDocumentoLegalizacionTerminalesValle2
                },
                'relatoria_taller_apertura': {
                    'modelo': RelatoriaTallerApertura,
                    'registro': RegistroRelatoriaTallerApertura
                },
                'relatoria_taller_administratic': {
                    'modelo': RelatoriaTallerAdministratic,
                    'registro': RegistroRelatoriaTallerAdministratic
                },
                'relatoria_taller_contenidos_educativos': {
                    'modelo': RelatoriaTallerContenidosEducativos,
                    'registro': RegistroRelatoriaTallerContenidosEducativos
                },
                'relatoria_taller_raee': {
                    'modelo': RelatoriaTallerRAEE,
                    'registro': RegistroRelatoriaTallerRAEE
                },
                'retoma': {
                    'modelo': Retoma,
                    'registro': RegistroRetoma
                }
            }

            for key in modelos.keys():
                modelo = modelos[key]['modelo']
                cantidad += modelo.objects.filter(red = self, estado__in = ['Nuevo','Actualizado']).count()

        elif self.estrategia == "Formación":


            asistencias_innovatic = ListadoAsistencia.objects.filter(red=self,grupo__estrategia__nombre='InnovaTIC',estado__in=["Nuevo", "Actualizado"])
            ple_innovatic = ProductoFinalPle.objects.filter(red=self, grupo__estrategia__nombre='InnovaTIC',estado__in=["Nuevo", "Actualizado"])
            asistencias_ruraltic = ListadoAsistencia.objects.filter(red=self,grupo__estrategia__nombre='RuralTIC',estado__in=["Nuevo", "Actualizado"])
            repositorio_ruraltic = RepositorioActividades.objects.filter(red=self,grupo__estrategia__nombre='RuralTIC',estado__in=["Nuevo", "Actualizado"])

            cantidad = asistencias_innovatic.count() + ple_innovatic.count() + asistencias_ruraltic.count() + repositorio_ruraltic.count()


        return cantidad


#------------------------------------- RETOMA -------------------------------------


def upload_dinamic_retomas(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Retomas', str(instance.id), filename])

class Retoma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING)

    fecha = models.DateField()
    radicado = models.CharField(max_length=100)

    dane = models.CharField(max_length=100,blank=True,null=True)
    sede_educativa = models.CharField(max_length=100,blank=True,null=True)

    rector = models.CharField(max_length=100,blank=True,null=True)
    celular = models.CharField(max_length=100,blank=True,null=True)
    cedula = models.BigIntegerField(blank=True,null=True)

    bolsas = models.IntegerField(default=0)
    bolsas_empacadas = models.IntegerField(default=0)
    cpu = models.IntegerField(default=0)
    trc = models.IntegerField(default=0)
    lcd = models.IntegerField(default=0)
    portatil = models.IntegerField(default=0)
    impresora = models.IntegerField(default=0)
    tableta = models.IntegerField(default=0)
    perifericos = models.IntegerField(default=0)
    estado = models.CharField(max_length=100,default="")
    estado_observacion = models.CharField(max_length=100, default="")

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_retomas,
        content_types=['application/pdf'],
        max_upload_size=20971520,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_retomas,
        content_types=['application/pdf'],
        max_upload_size=20971520,
        max_length=255
    )
    tipo = models.CharField(max_length=100, default='')


    def get_equipos_calculadora(self):
        equipos = self.cpu*0.5 + self.trc*0.5 + self.lcd*0.5 + self.portatil*0.1 + self.impresora*0.5 + self.tableta*0.033
        return equipos


    def get_equipos_calculadora_cpe(self):
        equipos = self.cpu*0.5 + self.trc*0.5 + self.lcd*0.5 + self.portatil*0.1 + self.impresora*0.5 + self.tableta*0.033
        return "{0:.2f}".format(equipos)


    def get_bolsas_calculadora_sican(self):
        bolsas = self.cpu*0.5 + self.trc*0.5 + self.lcd*0.5 + self.portatil*0.1 + self.impresora*0.5 + self.tableta*0.033
        if bolsas > 0.0 and bolsas < 1.0:
            return round(1)
        else:
            return round(bolsas)


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_file2(self):
        url = None
        try:
            url = self.file2.url
        except:
            pass
        return url


    def __str__(self):
        return self.radicado

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def pretty_print_url_file2(self):
        try:
            url = self.file2.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file2.name) +'</a>'


    def pretty_print_valor(self):
        return '0'

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRetoma.objects.filter(retoma=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRetoma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    retoma = models.ForeignKey(Retoma, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_retoma",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



#------------------------------------- SEDE ----------------------------------------


def upload_dinamic_legalizacion_propiedad_terminales(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Legalización propiedad terminales', str(instance.id), filename])

class DocumentoLegalizacionTerminales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_legalizacion_propiedad_terminales,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=200, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100,default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroDocumentoLegalizacionTerminales.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroDocumentoLegalizacionTerminales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoLegalizacionTerminales, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_legalizacion_propiedad_terminales",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_legalizacion_propiedad_terminales_valle_1(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Legalización propiedad terminales Valle 1', str(instance.id), filename])

class DocumentoLegalizacionTerminalesValle1(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_legalizacion_propiedad_terminales_valle_1,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=200, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100,default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroDocumentoLegalizacionTerminalesValle1.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroDocumentoLegalizacionTerminalesValle1(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoLegalizacionTerminalesValle1, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_legalizacion_propiedad_terminales_valle1",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_legalizacion_propiedad_terminales_valle_2(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Legalización propiedad terminales Valle 2', str(instance.id), filename])

class DocumentoLegalizacionTerminalesValle2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_legalizacion_propiedad_terminales_valle_2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=200, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100,default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroDocumentoLegalizacionTerminalesValle2.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroDocumentoLegalizacionTerminalesValle2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoLegalizacionTerminalesValle2, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_legalizacion_propiedad_terminales_valle2",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')






def upload_dinamic_encuesta_monitoreo(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Legalización propiedad terminales', str(instance.id), filename])

class EncuestaMonitoreo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_encuesta_monitoreo,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=200, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroEncuestaMonitoreo.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroEncuestaMonitoreo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(EncuestaMonitoreo, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_encuesta_monitoreo",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_relatoria_taller_apertura(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Relatoria taller apertura', str(instance.id), filename])

class RelatoriaTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_relatoria_taller_apertura,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRelatoriaTallerApertura.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRelatoriaTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RelatoriaTallerApertura, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_relatoria_taller_apertura",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_cuenticos_taller_apertura(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'CuenTICos taller apertura', str(instance.id), filename])

class CuenticosTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_cuenticos_taller_apertura,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroCuenticosTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(CuenticosTallerApertura, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_cuenticos_taller_apertura",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_registro_fotografico_taller_apertura(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Registro fotografico taller apertura', str(instance.id), filename])

class RegistroFotograficoTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_apertura,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_apertura,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_apertura,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_apertura,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_foto2(self):
        url = None
        try:
            url = self.foto2.url
        except:
            pass
        return url

    def url_foto3(self):
        url = None
        try:
            url = self.foto3.url
        except:
            pass
        return url

    def url_foto4(self):
        url = None
        try:
            url = self.foto4.url
        except:
            pass
        return url

    def get_fotos_list(self):
        fotos = []

        if self.url_foto1() != None:
            fotos.append(self.url_foto1())

        if self.url_foto2() != None:
            fotos.append(self.url_foto2())

        if self.url_foto3() != None:
            fotos.append(self.url_foto3())

        if self.url_foto4() != None:
            fotos.append(self.url_foto4())

        return fotos

class RegistroRegistroFotograficoTallerApertura(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RegistroFotograficoTallerApertura, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_registro_fotografico_taller_apertura",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_relatoria_taller_administratic(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Relatoria taller administratic', str(instance.id), filename])

class RelatoriaTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_relatoria_taller_administratic,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRelatoriaTallerAdministratic.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRelatoriaTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RelatoriaTallerAdministratic, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_relatoria_taller_administratic",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_infotic_taller_administratic(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'InfoTIC taller administratic', str(instance.id), filename])

class InfoticTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_infotic_taller_administratic,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroInfoticTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(InfoticTallerAdministratic, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_infotic_taller_administratic",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_registro_fotografico_taller_administratic(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Registro fotografico taller administratic', str(instance.id), filename])

class RegistroFotograficoTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_administratic,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_administratic,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_administratic,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_administratic,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_foto2(self):
        url = None
        try:
            url = self.foto2.url
        except:
            pass
        return url

    def url_foto3(self):
        url = None
        try:
            url = self.foto3.url
        except:
            pass
        return url

    def url_foto4(self):
        url = None
        try:
            url = self.foto4.url
        except:
            pass
        return url

    def get_fotos_list(self):
        fotos = []

        if self.url_foto1() != None:
            fotos.append(self.url_foto1())

        if self.url_foto2() != None:
            fotos.append(self.url_foto2())

        if self.url_foto3() != None:
            fotos.append(self.url_foto3())

        if self.url_foto4() != None:
            fotos.append(self.url_foto4())

        return fotos

class RegistroRegistroFotograficoTallerAdministratic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RegistroFotograficoTallerAdministratic, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_registro_fotografico_taller_administratic",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_relatoria_taller_contenidos_educativos(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Relatoria taller contenidos educativos', str(instance.id), filename])

class RelatoriaTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_relatoria_taller_contenidos_educativos,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRelatoriaTallerContenidosEducativos.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRelatoriaTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RelatoriaTallerContenidosEducativos, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_taller_contenidos_educativos",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_dibuarte_taller_contenidos_educativos(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'DibuARTE taller contenidos educativos', str(instance.id), filename])

class DibuarteTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_dibuarte_taller_contenidos_educativos,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroDibuarteTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DibuarteTallerContenidosEducativos, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_infotic_dibuarte_taller_contenidos_educativos",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_registro_fotografico_taller_contenidos_educativos(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Registro fotografico taller contenidos educativos', str(instance.id), filename])

class RegistroFotograficoTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_contenidos_educativos,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_contenidos_educativos,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_contenidos_educativos,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_contenidos_educativos,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_foto2(self):
        url = None
        try:
            url = self.foto2.url
        except:
            pass
        return url

    def url_foto3(self):
        url = None
        try:
            url = self.foto3.url
        except:
            pass
        return url

    def url_foto4(self):
        url = None
        try:
            url = self.foto4.url
        except:
            pass
        return url

    def get_fotos_list(self):
        fotos = []

        if self.url_foto1() != None:
            fotos.append(self.url_foto1())

        if self.url_foto2() != None:
            fotos.append(self.url_foto2())

        if self.url_foto3() != None:
            fotos.append(self.url_foto3())

        if self.url_foto4() != None:
            fotos.append(self.url_foto4())

        return fotos

class RegistroRegistroFotograficoTallerContenidosEducativos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RegistroFotograficoTallerContenidosEducativos, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_registro_fotografico_taller_contenidos_educativos",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_relatoria_taller_raee(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Relatoria taller RAEE', str(instance.id), filename])

class RelatoriaTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_relatoria_taller_raee,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRelatoriaTallerRAEE.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRelatoriaTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RelatoriaTallerRAEE, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_relatoria_taller_raee",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


def upload_dinamic_video_taller_raee(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Video Ecoraee taller RAEE', str(instance.id), filename])

class EcoraeeTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_video_taller_raee,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroEcoraeeTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(EcoraeeTallerRAEE, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_ecoraee_taller_raee",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_registro_fotografico_taller_raee(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Registro fotografico taller RAEE', str(instance.id), filename])

class RegistroFotograficoTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_raee,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_raee,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_raee,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_registro_fotografico_taller_raee,
        content_types=['image/jpg', 'image/jpeg', 'image/png'],
        max_upload_size=5242880,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    radicado = models.ForeignKey(Radicados, on_delete=models.DO_NOTHING, blank = True, null = True)

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_foto2(self):
        url = None
        try:
            url = self.foto2.url
        except:
            pass
        return url

    def url_foto3(self):
        url = None
        try:
            url = self.foto3.url
        except:
            pass
        return url

    def url_foto4(self):
        url = None
        try:
            url = self.foto4.url
        except:
            pass
        return url

    def get_fotos_list(self):
        fotos = []

        if self.url_foto1() != None:
            fotos.append(self.url_foto1())

        if self.url_foto2() != None:
            fotos.append(self.url_foto2())

        if self.url_foto3() != None:
            fotos.append(self.url_foto3())

        if self.url_foto4() != None:
            fotos.append(self.url_foto4())

        return fotos

class RegistroRegistroFotograficoTallerRAEE(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RegistroFotograficoTallerRAEE, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_registro_fotografico_taller_raee",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')





#------------------------------------- SEDE RUTA -------------------------------------


def upload_dinamic_evento_municipal(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Eventos municipales', str(instance.id), filename])

class EventoMunicipal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_evento_municipal,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="' + url + '"> ' + str(self.file.name) + '</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroEventoMunicipal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(EventoMunicipal, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_evento_municipal",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_evento_institucional(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Eventos institucionales', str(instance.id), filename])

class EventoInstitucional(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_evento_institucional,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100,default='')
    novedades = models.CharField(max_length=100,default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="' + url + '"> ' + str(self.file.name) + '</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroEventoInstitucional(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(EventoInstitucional, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_evento_institucional",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_acta_postulacion(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Concurso sedes', str(instance.id), filename])

class ActaPostulacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_postulacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroActaPostulacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ActaPostulacion, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_acta_postulacion",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_base_datos_postulante(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Base de datos postulante', str(instance.id), filename])

class BaseDatosPostulante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_postulacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroBaseDatosPostulante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(BaseDatosPostulante, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_base_datos_postulante",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_actualizacion_directorio_sedes(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Actualización directorio sedes', str(instance.id), filename])

class ActualizacionDirectorioSedes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_postulacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroActualizacionDirectorioSedes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ActualizacionDirectorioSedes, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_actualizacion_directorio_sedes",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_actualizacion_directorio_municipios(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Actualización directorio municipios', str(instance.id), filename])

class ActualizacionDirectorioMunicipios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_directorio_municipios,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroActualizacionDirectorioMunicipios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ActualizacionDirectorioMunicipios, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_actualizacion_directorio_municipios",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_cronograma_talleres(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Cronograma talleres', str(instance.id), filename])

class CronogramaTalleres(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_postulacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroCronogramaTalleres(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(CronogramaTalleres, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_cronograma_talleres",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_documento_legalizacion(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Documento legalización entrega tabletas a docentes', str(instance.id), filename])

class DocumentoLegalizacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_legalizacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100, default='')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroDocumentoLegalizacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoLegalizacion, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_documento_legalizacion",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_relatoria_graduacion_docentes(instance, filename):
    return '/'.join(['CPE 2018', 'Acceso', 'Relatoria graduación docentes', str(instance.id), filename])

class RelatoriaGraduacionDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_legalizacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_upload_size=52428800,
        max_length=255
    )

    ver = models.IntegerField(default=0)
    nombre = models.CharField(max_length=100,default='')
    novedades = models.CharField(max_length=100,default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

class RegistroRelatoriaGraduacionDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RelatoriaGraduacionDocentes, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_relatoria_graduacion_docentes",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




#----------------------------------- FORMACIÓN ------------------------------------

def upload_dinamic_documento_compromiso_inscripcion(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Documento Compromiso Inscripcion', str(instance.id), filename])

class DocumentoCompromisoInscripcion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_compromiso_inscripcion,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_1')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroDocumentoCompromisoInscripcion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoCompromisoInscripcion, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_documento_compromiso_inscripcion",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_acta_posesion_docente(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Acta de posesion docente', str(instance.id), filename])

class ActaPosesionDocente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_posesion_docente,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_2')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroActaPosesionDocente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ActaPosesionDocente, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_acta_posesion_docente",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_base_datos_docentes(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Base de datos docentes', str(instance.id), filename])

class BaseDatosDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_base_datos_docentes,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_3')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroBaseDatosDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(BaseDatosDocentes, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_base_datos_docentes",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_documento_proyeccion_cronograma(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Documento proyección cronograma', str(instance.id), filename])

class DocumentoProyeccionCronograma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_proyeccion_cronograma,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_4')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroDocumentoProyeccionCronograma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(DocumentoProyeccionCronograma, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_documento_proyeccion_cronograma",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_listado_asistencia(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Listado de Asistencia', str(instance.id), filename])

class ListadoAsistencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_listado_asistencia,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_5')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

    def get_fecha_actualizacion_estado(self):
        fecha = ''

        if self.estado == 'Nuevo' or self.estado == 'Actualizado':
            pass
        else:
            registros = RegistroListadoAsistencia.objects.filter(modelo = self).order_by('-creation')
            if registros.count() > 0:
                registro = registros[0]
                fecha = registro.creation.strftime('%d/%m/%Y')

        return fecha

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroListadoAsistencia.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroListadoAsistencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ListadoAsistencia, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_listado_asistencia",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_instrumento_autoreporte(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Instrumento Autoreporte', str(instance.id), filename])

class InstrumentoAutoreporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_instrumento_autoreporte,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_6')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroInstrumentoAutoreporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(InstrumentoAutoreporte, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_instrumento_autoreporte",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_presentacion_apa(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Presentación APA', str(instance.id), filename])

class PresentacionApa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_presentacion_apa,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_7')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroPresentacionApa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(PresentacionApa, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_presentacion_apa",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_instrumento_hagamos_memoria(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Instrumento hagamos memoria', str(instance.id), filename])

class InstrumentoHagamosMemoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_instrumento_hagamos_memoria,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_8')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroInstrumentoHagamosMemoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(InstrumentoHagamosMemoria, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_instrumento_hagamos_memoria",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_presentacion_actividad_pedagogica(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Presentacion actividad pedagogica', str(instance.id), filename])

class PresentacionActividadPedagogica(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_presentacion_actividad_pedagogica,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_9')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroPresentacionActividadPedagogica(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(PresentacionActividadPedagogica, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_presentacion_actividad_pedagogica",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_repositorio_actividades(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Repositorio actividades', str(instance.id), filename])

class RepositorioActividades(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_repositorio_actividades,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_10')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

    def get_fecha_actualizacion_estado(self):
        fecha = ''

        if self.estado == 'Nuevo' or self.estado == 'Actualizado':
            pass
        else:
            registros = RegistroRepositorioActividades.objects.filter(modelo = self).order_by('-creation')
            if registros.count() > 0:
                registro = registros[0]
                fecha = registro.creation.strftime('%d/%m/%Y')

        return fecha

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroRepositorioActividades.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroRepositorioActividades(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(RepositorioActividades, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_repositorio_actividades",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_sistematizacion_experiencia(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Sistematizacion experiencia', str(instance.id), filename])

class SistematizacionExperiencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_sistematizacion_experiencia,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_11')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroSistematizacionExperiencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(SistematizacionExperiencia, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_sistematizacion_experiencia",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_instrumento_evaluacion(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Instrumento Evaluacion', str(instance.id), filename])

class InstrumentoEvaluacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_instrumento_evaluacion,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_12')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroInstrumentoEvaluacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(InstrumentoEvaluacion, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_instrumento_evaluacion",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')




def upload_dinamic_instrumento_estructuracion_ple(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Instrumento estructuración PLE', str(instance.id), filename])

class InstrumentoEstructuracionPle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_instrumento_estructuracion_ple,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True, related_name='rechazados_13')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

class RegistroInstrumentoEstructuracionPle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(InstrumentoEstructuracionPle, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_instrumento_estructuracion_ple",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_producto_final_ple(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Producto final PLE', str(instance.id), filename])

class ProductoFinalPle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    red = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True)
    grupo = models.ForeignKey(Grupos, on_delete=models.DO_NOTHING)
    entregable = models.ForeignKey(Entregables, on_delete=models.DO_NOTHING)
    fecha = models.DateField()

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_producto_final_ple,
        max_upload_size=52428800,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png',
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        max_length=255
    )

    ver = models.IntegerField(default=0)
    docentes = models.ManyToManyField(Docentes)
    docentes_rechazados = models.ManyToManyField(Docentes, blank=True,related_name='rechazados_14')
    novedades = models.CharField(max_length=100, default='')
    valor = models.IntegerField(default=0)
    estado = models.CharField(max_length=100, default="")
    eliminar = models.BooleanField(default=False)
    tipo = models.CharField(max_length=100, default='')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

    def get_extension(self):
        return self.file.name.split('.')[-1]

    def get_valor(self, entregable):

        ids_docentes = self.docentes.all().values_list('id',flat=True)

        valor = EntregableRutaObject.objects.filter(
            entregable = entregable,
            docente__id__in = ids_docentes).aggregate(Sum('valor'))['valor__sum']

        if valor == None:
            valor = 0

        return '${:20,.2f}'.format(valor)

    def get_fecha_actualizacion_estado(self):
        fecha = ''

        if self.estado == 'Nuevo' or self.estado == 'Actualizado':
            pass
        else:
            registros = RegistroProductoFinalPle.objects.filter(modelo = self).order_by('-creation')
            if registros.count() > 0:
                registro = registros[0]
                fecha = registro.creation.strftime('%d/%m/%Y')

        return fecha

    def get_observaciones(self):

        observacion = ''
        html_observacion = ''
        registros = RegistroProductoFinalPle.objects.filter(modelo=self).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            html_observacion += html.render(delta_obj['ops'])

        observacion = html2text.html2text(html_observacion)

        return observacion

class RegistroProductoFinalPle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    modelo = models.ForeignKey(ProductoFinalPle, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_producto_final_ple",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')
#----------------------------------------------------------------------------------


def upload_dinamic_actualizacion_lupaap(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Actualización Lupaap', str(instance.id), filename])

class ActualizacionLupaap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)

    tablero_control = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_lupaap,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255
    )

    tablero_control_json = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_lupaap,
        max_upload_size=52428800,
        content_types=[
            'application/json',
        ],
        max_length=255,
        blank=True,
        null=True
    )

    informe_lupaap = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_lupaap,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255
    )

    informe_lupaap_json = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_lupaap,
        max_upload_size=52428800,
        content_types=[
            'application/json',
        ],
        max_length=255,
        blank=True,
        null=True
    )

    resultado = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_lupaap,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255,
        blank = True,
        null = True
    )

    red_r2 = models.ForeignKey(Red,on_delete=models.DO_NOTHING,blank=True,null=True,related_name='red_r2_actualizacion')
    red_r3 = models.ForeignKey(Red, on_delete=models.DO_NOTHING, blank=True, null=True,related_name='red_r3_actualizacion')

    def construir(self):
        tasks.calcular_actualizacion.delay(str(self.id))
        return 'Ok'


def upload_dinamic_actualizacion_autoreporte_evaluacion(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Actualización Autoreporte y Evaluacion', str(instance.id), filename])

class ActualizacionAutoreporteEvaluacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)

    tablero_control = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_autoreporte_evaluacion,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255
    )

    tablero_control_json = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_autoreporte_evaluacion,
        max_upload_size=52428800,
        content_types=[
            'application/json',
        ],
        max_length=255,
        blank=True,
        null=True
    )



    resultado = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_autoreporte_evaluacion,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255,
        blank = True,
        null = True
    )

    def construir(self):
        tasks.calcular_actualizacion_autoreporte_evaluacion(str(self.id))
        return 'Ok'


def upload_dinamic_actualizacion_productos_finales(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'Actualización Productos Finales', str(instance.id), filename])

class ActualizacionProductosFinales(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)

    tablero_control = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_productos_finales,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255
    )

    tablero_control_json = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_productos_finales,
        max_upload_size=52428800,
        content_types=[
            'application/json',
        ],
        max_length=255,
        blank=True,
        null=True
    )



    resultado = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_actualizacion_productos_finales,
        max_upload_size=52428800,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_length=255,
        blank = True,
        null = True
    )

    def construir(self):
        tasks.calcular_actualizacion_productos_finales(str(self.id))
        return 'Ok'