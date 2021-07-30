from django.db import models
import uuid
from usuarios.models import Municipios, User, Departamentos, Corregimientos, Veredas, PueblosIndigenas, \
    ResguardosIndigenas, ComunidadesIndigenas, LenguasNativas, ConsejosAfro, ComunidadesAfro, CategoriaDiscapacidad, \
    DificultadesPermanentesDiscapacidad, ElementosDiscapacidad, TiposRehabilitacionDiscapacidad

from recursos_humanos import models as models_rh
from djmoney.models.fields import MoneyField
from django.db.models import Sum
from direccion_financiera.models import Bancos
from config.extrafields import ContentTypeRestrictedFileField
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone
from django.conf import settings
import json
from delta import html
from django.contrib.postgres.fields import JSONField




settings_time_zone = timezone(settings.TIME_ZONE)

# Create your models here.

class Componentes(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    consecutivo = models.IntegerField()
    momentos = models.IntegerField()
    valor = models.IntegerField(default=0)
    ruta = models.TextField(default='')
    valor_pagado = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def get_numero_momentos(self):
        return Momentos.objects.filter(componente=self).count()


    def get_cantidad_instrumentos(self,hogar):
        return InstrumentosRutaObject.objects.filter(hogar = hogar,momento__componente = self).count()


    def get_valor_hogar(self, hogar):
        valor = CuposRutaObject.objects.filter(hogar=hogar, momento__componente = self,estado__in=['Reportado','Pagado']).aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0


    def get_ruta_hogar_componente(self, hogar):

        if self.consecutivo == 1:
            return hogar.ruta_1
        elif self.consecutivo == 2:
            return hogar.ruta_2
        elif self.consecutivo == 3:
            return hogar.ruta_3
        elif self.consecutivo == 4:
            return hogar.ruta_4
        else:
            return None

class Momentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    componente = models.ForeignKey(Componentes,on_delete=models.DO_NOTHING,related_name='momentos_componente_fest_2020')
    nombre = models.CharField(max_length=100)
    consecutivo = models.IntegerField()
    instrumentos = models.IntegerField()
    tipo = models.CharField(max_length=100)
    valor_maximo = models.BooleanField(default=True)
    novedades = models.BooleanField(default=True)
    progreso = models.BooleanField(default=True)
    meta = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '{0} - {1}'.format(self.componente.nombre,self.nombre)


    def get_objetos_ruta(self,ruta):
        return CuposRutaObject.objects.filter(momento = self, ruta = ruta).count()


    def get_cantidad_instrumentos(self,hogar,componente):
        return InstrumentosRutaObject.objects.filter(hogar = hogar,momento__componente = componente, momento = self).count()

    def get_novedades_mis_rutas_actividades(self,ruta):
        return InstrumentosRutaObject.objects.filter(ruta = ruta, momento = self, estado = 'cargado').distinct().count()

    def get_numero_instrumentos(self):
        return Instrumentos.objects.filter(momento=self).count()

    def get_consecutivo(self):
        return '{0}.{1}'.format(self.componente.consecutivo,self.consecutivo)

    def get_valor_maximo_momento(self,ruta):



        try:
            data = json.loads(ruta.valores_actividades)
        except:
            data = []


        if 'valor_' + str(self.id) in data:
            valor = data['valor_' + str(self.id)].replace('$ ','').replace(',','')

        else:
            valor = 0

        return float(valor)


    def get_cantidad_momento(self,ruta):



        try:
            data = json.loads(ruta.valores_actividades)
        except:
            data = []


        if 'cantidad_' + str(self.id) in data:
            cantidad = data['cantidad_' + str(self.id)]

        else:
            cantidad = 0

        return cantidad


    def get_valor_maximo_momento_corte(self,ruta,corte):
        valor = CuposRutaObject.objects.filter(ruta = ruta, momento = self, corte = corte).aggregate(Sum('valor'))['valor__sum']
        if valor == None:
            valor = 0
        return float(valor)


    def get_valor_reportado_momento(self,ruta):
        valor = CuposRutaObject.objects.filter(ruta = ruta, momento = self, estado = 'Reportado').aggregate(Sum('valor'))['valor__sum']
        if valor == None:
            valor = 0
        return float(valor)

    def get_valor_pagado_momento(self,ruta):
        valor = CuposRutaObject.objects.filter(ruta = ruta, momento = self, estado = 'Pagado').aggregate(Sum('valor'))['valor__sum']
        if valor == None:
            valor = 0
        return float(valor)

    def get_progreso_momento(self,ruta):

        query = InstrumentosRutaObject.objects.filter(ruta=ruta, momento=self)

        hogares__ids = query.filter(estado__in=['aprobado']).values_list('hogares__id',flat=True)

        hogares = Hogares.objects.filter(id__in = hogares__ids)

        try:
            progreso = (hogares.count() / ruta.meta) * 100.0
        except:
            progreso = 0


        return progreso



    def get_progreso_momento_escalado(self,ruta,escala):

        query = InstrumentosRutaObject.objects.filter(ruta=ruta, momento=self)

        hogares__ids = query.filter(estado__in=['aprobado']).values_list('hogares__id',flat=True)

        hogares = Hogares.objects.filter(id__in = hogares__ids)

        try:
            progreso = (hogares.count() / ruta.meta) * 100.0
        except:
            progreso = 0


        try:
            escalado = (progreso*escala)/100.0
        except:
            escalado = 0


        return escalado




    def get_progreso_reportado(self, ruta, exclude):

        query = CuposRutaObject.objects.filter(ruta = ruta)

        if exclude != None:
            query = query.exclude(id = exclude.id)

        progreso = 0

        for cupo in query:
            progreso += cupo.data[f'valor_meta_{self.meta}_{self.id}']

        return progreso

    def get_progreso_pendiente(self, ruta, exclude):
        return 0


    def get_valor_pagado(self,hogar):
        query = CuposRutaObject.objects.filter(momento = self, estado__in = ['Reportado','Pagado'], hogar = hogar)
        valor = query.aggregate(Sum('valor'))['valor__sum']
        if valor == None:
            valor = 0

        return valor

class Instrumentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    momento = models.ForeignKey(Momentos,on_delete=models.DO_NOTHING,related_name='instrumento_momento_fest_2020_1')
    nombre = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)
    consecutivo = models.IntegerField()
    modelo = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    nivel = models.CharField(max_length=100)
    meta = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nombre

    def get_consecutivo(self):
        return '{0}.{1}.{2}'.format(self.momento.componente.consecutivo,self.momento.consecutivo,self.consecutivo)

class Rutas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    nombre = models.CharField(unique=True, max_length=100)
    contrato = models.ForeignKey(models_rh.Contratos, on_delete=models.DO_NOTHING,
                                 related_name='contrato_ruta_fest_2020')
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP',default=0)
    valor_transporte = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0)
    valor_otros = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0)

    novedades = models.IntegerField(default=0)
    meta = models.PositiveIntegerField(default=0)
    progreso = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_ruta_fest_2020", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_ruta_fest_2020",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    estado = models.CharField(max_length=100,blank=True)
    componente = models.ForeignKey(Componentes, on_delete=models.DO_NOTHING,blank=True,null=True)

    hogares_inscritos = models.IntegerField(default=0)

    tipo_pago = models.CharField(max_length=100,default="actividad")
    valores_actividades = models.TextField()
    visible = models.BooleanField(default=True)


    def __str__(self):
        return self.nombre



    def get_liquidacion(self):

        liquidacion = None

        try:
            liquidacion = Liquidaciones.objects.get(ruta = self)
        except:
            pass

        return liquidacion


    def calcular_valor(self, cleaned_data):
        try:
            valores_actividades = json.loads(self.valores_actividades)
        except:
            valores_actividades = []

        valor = 0

        for key in cleaned_data:
            momento = Momentos.objects.get(id = key.split('_')[-1])
            valor_meta = float(valores_actividades['valor_meta_'+str(momento.meta)].replace('$ ', '').replace(',',''))
            valor += valor_meta * (cleaned_data[key]/100)

        return valor

    def get_valor_pagado_ruta(self):
        valor = CuposRutaObject.objects.filter(ruta = self,estado__in = ["Pagado","Reportado"]).aggregate(Sum('valor'))['valor__sum']
        if valor == None:
            valor = 0
        return '$ {:20,.2f}'.format(valor)

    def get_cupos_ruta_object(self):

        data = {}
        cupos = CuposRutaObject.objects.filter(ruta=self)

        return data


    def get_aprobable_valor(self, momento):

        dict = {'aprobable': 'no','valor': 0}

        if self.tipo_pago == 'actividad':

            valores_actividades = json.loads(self.valores_actividades)

            try:
                cantidad = int(valores_actividades['cantidad_' + str(momento.id)])
            except:
                cantidad = 0

            try:
                valor = float(valores_actividades['valor_' + str(momento.id)].replace("$ ",'').replace(',',''))
            except:
                valor = float(0)


            objetos_aprobados = CuposRutaObject.objects.filter(ruta = self, momento = momento, estado__in = ["aprobado","Reportado","Pagado"])
            valor_aprobados = objetos_aprobados.aggregate(Sum('valor'))['valor__sum']

            if valor_aprobados == None:
                valor_aprobados = float(0)
            else:
                valor_aprobados = float(valor_aprobados)

            if objetos_aprobados.count() < cantidad:

                try:
                    valor_actividad = (valor - valor_aprobados) / (cantidad - objetos_aprobados.count())
                except:
                    valor_actividad = 0


                dict['aprobable']= 'si'
                dict['valor']= valor_actividad



        else:
            pass

        return dict

    def translado(self, hogar, componente):

        update = False

        momentos_ids = []

        for cupo in CuposRutaObject.objects.filter(hogar = hogar, estado__in = ['Pagado','Reportado'], translado = False,momento__componente = componente).exclude(ruta=self):

            if cupo.momento.id not in momentos_ids:

                update = True

                CuposRutaObject.objects.get_or_create(
                    ruta = self,
                    momento = cupo.momento,
                    tipo = cupo.tipo,
                    estado = 'Pagado',
                    valor = 0,
                    hogar = cupo.hogar,
                    translado = False
                )

            cupo.translado = True
            cupo.save()

        ruta = None

        if componente.consecutivo == 1:

            if hogar.ruta_1 != None:
                ruta = hogar.ruta_1

            hogar.ruta_1 = self
            hogar.save()

        elif componente.consecutivo == 2:

            if hogar.ruta_2 != None:
                ruta = hogar.ruta_2

            hogar.ruta_2 = self
            hogar.save()

        elif componente.consecutivo == 3:

            if hogar.ruta_3 != None:
                ruta = hogar.ruta_3

            hogar.ruta_3 = self
            hogar.save()

        elif componente.consecutivo == 4:

            if hogar.ruta_4 != None:
                ruta = hogar.ruta_4

            hogar.ruta_4 = self
            hogar.save()

        if ruta != None:
            ruta.update_hogares_inscritos()
            if update:
                ruta.actualizar_objetos()

        return update

    def translado_vinculacion(self, hogar):

        update = False

        momentos_ids = []

        for cupo in CuposRutaObject.objects.filter(hogar = hogar, estado__in = ['Pagado','Reportado'], translado = False, momento__tipo = 'vinculacion').exclude(ruta=self):

            if cupo.momento.id not in momentos_ids:

                update = True

                CuposRutaObject.objects.get_or_create(
                    ruta = self,
                    momento = cupo.momento,
                    tipo = cupo.tipo,
                    estado = 'Pagado',
                    valor = 0,
                    hogar = cupo.hogar,
                    translado = False
                )

            cupo.translado = True
            cupo.save()

        ruta = None


        if hogar.ruta_vinculacion != None:
            ruta = hogar.ruta_vinculacion

        hogar.ruta_vinculacion = self
        hogar.save()



        if ruta != None:
            ruta.update_hogares_inscritos()
            if update:
                ruta.actualizar_objetos()

        return update

    def update_visita_1(self):

        momento = Momentos.objects.filter(componente = self.componente).get(nombre = "Visita 1")
        valor_total = CuposRutaObject.objects.filter(ruta = self,momento = momento).aggregate(Sum('valor'))['valor__sum']
        CuposRutaObject.objects.filter(ruta = self, momento= momento, estado = "asignado").delete()
        asignados = CuposRutaObject.objects.filter(ruta=self,momento=momento).count()

        for i in range(0,self.meta_vinculacion-asignados):

            CuposRutaObject.objects.create(
                ruta=self,
                momento=momento,
                tipo=momento.tipo,
                estado='asignado',
                valor=0
            )

        objetos = CuposRutaObject.objects.filter(ruta=self,momento=momento)
        valor = valor_total/objetos.count()
        objetos.update(valor=valor)

        return '{0} - {1}'.format(self.meta_vinculacion,objetos.count())

    def update_progreso(self):

        query = InstrumentosRutaObject.objects.filter(ruta=self)
        momentos = Momentos.objects.filter(componente=self.componente).exclude(meta = 0)

        hogares__ids = query.filter(estado__in=['aprobado']).values_list('hogares__id', flat=True)

        hogares = Hogares.objects.filter(id__in=hogares__ids)

        try:
            progreso = (hogares__ids.count()/(self.meta * momentos.count()))*100.0
        except:
            progreso = 0

        self.progreso = progreso
        self.save()

        return self.progreso

    def set_novedades_ruta(self):
        novedades = 0
        for momento in Momentos.objects.filter(componente = self.componente):
            novedades += momento.get_novedades_mis_rutas_actividades(self)
        Rutas.objects.filter(id = self.id).update(novedades = novedades)
        self.update_progreso()
        return novedades

    def update_novedades(self):
        self.novedades = InstrumentosRutaObject.objects.filter(ruta=self, estado='cargado').count()
        self.save()
        self.update_progreso()
        return 'Ok'

    def update_hogares_inscritos(self):

        objetos_hogares = Hogares.objects.filter(rutas = self)

        self.hogares_inscritos = objetos_hogares.count()
        self.save()

        return None

    def crear_objetos_momento(self,momento,procesados,meta,valor,cantidad_momentos,meta_vinculacion):

        valor = valor/cantidad_momentos

        valor_procesados = procesados.filter(momento=momento).aggregate(Sum('valor'))['valor__sum']
        if valor_procesados == None:
            valor_procesados = 0

        nueva_meta = (meta - procesados.filter(momento=momento).exclude(translado = True).count())



        try:
            nuevo_valor = (valor - float(valor_procesados)) / (nueva_meta)
        except:
            return (0,0)

        else:
            if momento.nombre == 'Visita 1':

                nueva_meta_visita_1 = (meta_vinculacion - procesados.filter(momento=momento).count())

                try:
                    nuevo_valor_visita_1 = (valor - float(valor_procesados)) / (nueva_meta_visita_1)
                except:
                    return (0, 0)

                for i in range(0, nueva_meta_visita_1):
                    CuposRutaObject.objects.create(
                        ruta=self,
                        momento=momento,
                        tipo=momento.tipo,
                        estado='asignado',
                        valor=nuevo_valor_visita_1
                    )
            else:
                for i in range(0, nueva_meta):
                    CuposRutaObject.objects.create(
                        ruta=self,
                        momento=momento,
                        tipo=momento.tipo,
                        estado='asignado',
                        valor=nuevo_valor
                    )

            return (nueva_meta,nuevo_valor)

    def clean_objetos(self,tipo):

        CuposRutaObject.objects.filter(ruta=self, estado = "asignado",momento__tipo = tipo).delete()
        procesados = CuposRutaObject.objects.filter(ruta = self, estado__in = ["Reportado","Pagado"], momento__tipo = tipo)

        return procesados

    def actualizar_objetos(self):

        tipos = {
            'vinculacion':{'meta':self.meta_vinculacion,'valor':float(self.valor_vinculacion.amount)},
            'visita': {'meta': self.meta_hogares, 'valor': (float(self.valor_actividades.amount)*self.peso_visitas)/100},
            'encuentro': {'meta': self.meta_hogares, 'valor': (float(self.valor_actividades.amount)*self.peso_encuentros)/100},
            'otros': {'meta': self.meta_hogares, 'valor': (float(self.valor_actividades.amount) * self.peso_otros)/100},
        }
        momentos = Momentos.objects.filter(componente=self.componente)

        #for key in tipos.keys():

        #    procesados = self.clean_objetos(key)

        #    cantidad_momentos = momentos.filter(tipo=key).count()

        #    for momento in momentos.filter(tipo=key):

        #        meta,valor = self.crear_objetos_momento(momento,procesados,tipos[key]['meta'],tipos[key]['valor'],cantidad_momentos,self.meta_vinculacion)


        if tipos['vinculacion']['meta'] > 0:

            for key in tipos.keys():

                valor_total = tipos[key]['valor'] # valor total del tipo de momento
                cantidad_momentos = momentos.filter(tipo=key).count() # cantidad total de momentos del componente
                procesados = self.clean_objetos(key) #query de objetos pagos o reportados
                valor_procesados = procesados.aggregate(Sum('valor'))['valor__sum']
                if valor_procesados == None:
                    valor_procesados = 0


                nueva_meta = (cantidad_momentos * tipos[key]['meta']) - procesados.filter(ruta = self).exclude(translado=True).count()
                nuevo_valor_total = valor_total - float(valor_procesados)




                try:
                    valor_momento = nuevo_valor_total / nueva_meta
                except:
                    pass

                else:

                    for momento in momentos.filter(tipo=key):

                        if momento.nombre == 'Visita 1':
                            nueva_meta_visita_1 = (tipos['vinculacion']['meta'] - procesados.filter(ruta = self,momento=momento).exclude(translado = True).count())

                            try:
                                nuevo_valor_visita_1 = (nuevo_valor_total/cantidad_momentos)/ nueva_meta_visita_1
                            except:
                                pass
                            else:

                                for i in range(0, nueva_meta_visita_1):
                                    CuposRutaObject.objects.create(
                                        ruta=self,
                                        momento=momento,
                                        tipo=momento.tipo,
                                        estado='asignado',
                                        valor=0
                                    )
                        else:
                            for i in range(0, tipos[key]['meta'] - procesados.filter(ruta = self,momento=momento).exclude(translado = True).count()):
                                CuposRutaObject.objects.create(
                                    ruta=self,
                                    momento=momento,
                                    tipo=momento.tipo,
                                    estado='asignado',
                                    valor=0
                                )


        else:

            for key in tipos.keys():

                valor_total = tipos[key]['valor']  # valor total del tipo de momento
                cantidad_momentos = momentos.filter(tipo=key).exclude(nombre = 'Visita 1').count()  # cantidad total de momentos del componente
                procesados = self.clean_objetos(key)  # query de objetos pagos o reportados
                valor_procesados = procesados.aggregate(Sum('valor'))['valor__sum']
                if valor_procesados == None:
                    valor_procesados = 0

                nueva_meta = (cantidad_momentos * tipos[key]['meta']) - procesados.filter(ruta=self).exclude(translado=True).exclude(momento__nombre="Visita 1").count()
                nuevo_valor_total = valor_total - float(valor_procesados)

                try:
                    valor_momento = nuevo_valor_total / nueva_meta
                except:
                    pass

                else:

                    print("Valor total: {0}".format(valor_total))

                    for momento in momentos.filter(tipo=key).exclude(nombre = 'Visita 1'):

                        for i in range(0,tipos[key]['meta'] - procesados.filter(ruta=self, momento=momento).exclude(translado=True).count()):
                            CuposRutaObject.objects.create(
                                ruta=self,
                                momento=momento,
                                tipo=momento.tipo,
                                estado='asignado',
                                valor=0
                            )


        for key in tipos.keys():

            valor_total = tipos[key]['valor']

            valor_pagados = CuposRutaObject.objects.filter(ruta = self, estado__in = ["Reportado","Pagado"], momento__tipo = key).aggregate(Sum('valor'))['valor__sum']


            if valor_pagados == None:
                valor_pagados = 0


            if valor_total > valor_pagados:

                valor_dividir = float(valor_total) - float(valor_pagados)

                objetos_creados = CuposRutaObject.objects.filter(ruta=self, estado = 'asignado', tipo = key)

                if objetos_creados.count() > 0:

                    valor_objeto = valor_dividir/objetos_creados.count()

                    objetos_creados.update(valor = valor_objeto)


        #valor_total = 0

        #for key in tipos.keys():
        #    valor_total += float(tipos[key]['valor'])


        #valor_objetos = CuposRutaObject.objects.filter(ruta = self).aggregate(Sum('valor'))['valor__sum']

        #if valor_objetos == None:
        #    valor_objetos = float(0)

        #else:
        #    valor_objetos = float(valor_objetos)


        #if valor_objetos < valor_total:

        #    adicional = valor_total - valor_objetos


        #    cantidad = CuposRutaObject.objects.filter(ruta = self, estado = 'asignado').count()


        #    if cantidad > 0:

        #        sumando = adicional / cantidad

        #        for cupo in CuposRutaObject.objects.filter(ruta = self, estado = 'asignado'):

        #            cupo.valor = float(cupo.valor.amount) + float(sumando)
        #            cupo.save()



        return 'Ok'

    def get_instrumentos_list(self,momento):

        instrumentos_return = []

        for instrumento in Instrumentos.objects.filter(momento = momento).order_by('consecutivo'):
            instrumentos_return.append({
                'id': instrumento.id,
                'short_name': instrumento.short_name,
                'icon': instrumento.icon,
                'color': instrumento.color
            })

        return instrumentos_return

    def get_valor_corte(self):
        objetos = CuposRutaObject.objects.filter(estado = "Reportado", ruta = self).exclude(momento__tipo = 'vinculacion')
        valor = objetos.aggregate(Sum('valor'))['valor__sum']
        return valor if \
            valor != None \
            else 0

    def get_valor_liquidacion(self):
        objetos = CuposRutaObject.objects.filter(estado__in = ["Reportado","Liquidado"], ruta = self).exclude(momento__tipo = 'vinculacion')
        valor = objetos.aggregate(Sum('valor'))['valor__sum']
        return valor if \
            valor != None \
            else 0


    def get_cupo_componente(self,componente):

        if componente.consecutivo == 1:
            cupos = self.meta_hogares - Hogares.objects.filter(ruta_1=self).count()

        elif componente.consecutivo == 2:
            cupos = self.meta_hogares - Hogares.objects.filter(ruta_2=self).count()

        elif componente.consecutivo == 3:
            cupos = self.meta_hogares - Hogares.objects.filter(ruta_3=self).count()

        elif componente.consecutivo == 4:
            cupos = self.meta_hogares - Hogares.objects.filter(ruta_4=self).count()

        else:
            cupos = 0

        return cupos


    def get_cupo_vinculacion(self):

        cupos = self.meta_vinculacion - Hogares.objects.filter(ruta_vinculacion=self).count()

        return cupos

class Hogares(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    documento = models.BigIntegerField(unique=True)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, related_name='hogares_municipio_inscripcion_fest_2020')

    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100,blank=True,null=True)
    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100,blank=True,null=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=100,blank=True,null=True)
    celular1 = models.CharField(max_length=100,blank=True,null=True)
    celular2 = models.CharField(max_length=100,blank=True,null=True)
    municipio_residencia = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, related_name='hogares_municipio_residencia_fest_2020')

    rutas = models.ManyToManyField(Rutas, related_name='rutas_fest_2020',blank=True)


    def __str__(self):
        return self.get_nombres() + ' ' + self.get_apellidos() + ' - ' + str(self.documento)


    def get_estado_momento(self, momento, ruta):

        instrumentos = InstrumentosRutaObject.objects.filter(momento = momento, hogares=self, ruta=ruta).order_by('creacion')

        try:
            estado = instrumentos[0].estado
        except:
            estado = ''

        return estado

    def get_gestor_momento(self, momento):

        instrumentos = InstrumentosRutaObject.objects.filter(momento=momento, hogares=self).order_by('creacion')

        try:
            gestor = instrumentos[0].ruta.contrato.contratista.get_full_name()
        except:
            gestor = ''

        return gestor

    def get_gestor_cedula_momento(self, momento):

        instrumentos = InstrumentosRutaObject.objects.filter(momento=momento, hogares=self).order_by('creacion')

        try:
            gestor = instrumentos[0].ruta.contrato.contratista.get_cedula()
        except:
            gestor = ''

        return gestor

    def get_ruta_momento(self, momento):

        instrumentos = InstrumentosRutaObject.objects.filter(momento=momento, hogares=self).order_by('creacion')

        try:
            ruta = instrumentos[0].ruta.nombre
        except:
            ruta = ''

        return ruta


    def get_rutas(self):

        rutas = ''

        for ruta in self.rutas.all():
            rutas += ruta.nombre + ', '

        if rutas != '':
            rutas = rutas[:-2]

        return rutas


    def get_estado_tablero(self, momento):
        estado = ''

        if CuposRutaObject.objects.filter(momento=momento, hogares=self).count() > 0:
            obj = CuposRutaObject.objects.filter(momento=momento, hogares=self).order_by('-valor')[0]
            estado = obj.estado + ', ' + obj.ruta.nombre + ', ' + str(obj.valor)

        return estado


    def get_valor_ruta_vinculacion(self):
        valor = CuposRutaObject.objects.filter(hogar=self,momento__tipo='vinculacion',estado__in=['Reportado','Pagado']).aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_nombre_ruta_componente(self,componente):


        ruta = ''


        if componente.consecutivo == 1:
            if self.ruta_1 != None:
                ruta = self.ruta_1.nombre

        elif componente.consecutivo == 2:
            if self.ruta_2 != None:
                ruta = self.ruta_2.nombre

        elif componente.consecutivo == 3:
            if self.ruta_3 != None:
                ruta = self.ruta_3.nombre

        elif componente.consecutivo == 4:
            if self.ruta_4 != None:
                ruta = self.ruta_4.nombre

        return ruta

    def get_ruta_componente(self,componente):


        ruta = None


        if componente.consecutivo == 1:
            if self.ruta_1 != None:
                ruta = self.ruta_1

        elif componente.consecutivo == 2:
            if self.ruta_2 != None:
                ruta = self.ruta_2

        elif componente.consecutivo == 3:
            if self.ruta_3 != None:
                ruta = self.ruta_3

        elif componente.consecutivo == 4:
            if self.ruta_4 != None:
                ruta = self.ruta_4

        return ruta

    def get_nombre_ruta_vinculacion(self):

        ruta = ''

        if self.ruta_vinculacion != None:
            ruta = self.ruta_vinculacion.nombre

        return ruta

    def get_ruta_vinculacion(self):

        ruta = None

        if self.ruta_vinculacion != None:
            ruta = self.ruta_vinculacion

        return ruta

    def get_vinculacion_ruta(self, ruta):
        respuesta = 'No'

        if self.ruta_vinculacion == ruta:
            respuesta = 'Si'

        return respuesta

    def get_estado_valor(self,ruta,momento):
        estado = ''
        try:
            obj = CuposRutaObject.objects.get(ruta=ruta,momento=momento,hogar=self)
        except:
            pass
        else:
            estado = str(obj.valor).replace('COL','')
        return estado

    def get_estado(self,ruta,momento):
        estado = ''
        try:
            obj = CuposRutaObject.objects.get(ruta=ruta,momento=momento,hogar=self)
        except:
            pass
        else:
            estado = obj.estado
        return estado

    def get_cantidad_instrumentos(self):
        return InstrumentosRutaObject.objects.filter(hogar = self).count()

    def get_novedades_mis_rutas_momento(self,ruta,momento):
        return InstrumentosRutaObject.objects.filter(ruta = ruta, momento = momento, hogar = self, estado__in = ['cargado','preaprobado']).count()

    def get_nombres(self):
        if self.segundo_nombre != None:
            nombres = '{0} {1}'.format(self.primer_nombre,self.segundo_nombre)
        else:
            nombres = self.primer_nombre
        return nombres

    def get_apellidos(self):
        if self.segundo_apellido != None:
            apellidos = '{0} {1}'.format(self.primer_apellido,self.segundo_apellido)
        else:
            apellidos = self.primer_apellido
        return apellidos

    def get_full_name(self):
        return '{0} {1}'.format(self.get_nombres(),self.get_apellidos())


    def get_gull_name(self):
        return '{0} {1}'.format(self.get_nombres(),self.get_apellidos())

    def get_valor_total(self):
        valor = CuposRutaObject.objects.filter(hogar=self).aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_cantidad_componentes(self):
        return CuposRutaObject.objects.filter(hogar=self).values_list('momento__componente__id',flat=True).distinct().count()

    def get_valor_vinculacion(self):
        valor = CuposRutaObject.objects.filter(hogar=self,momento__tipo='vinculacion').aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0

    def get_estado_tablero(self, momento):
        estado = ''

        if CuposRutaObject.objects.filter(momento=momento, hogar=self).count() > 0:
            obj = CuposRutaObject.objects.filter(momento=momento, hogar=self).order_by('-valor')[0]
            estado = obj.estado + ', ' + obj.ruta.nombre + ', ' + str(obj.valor)

        return estado

class PermisosCuentasRutas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING,related_name='user_permiso_cuent_fest_2020')
    rutas_ver = models.ManyToManyField(Rutas,related_name="permisos_cuentas_ver_fest_2020",blank=True)
    rutas_preaprobar = models.ManyToManyField(Rutas,related_name="permisos_cuentas_preaprobar_fest_2020",blank=True)
    rutas_aprobar = models.ManyToManyField(Rutas,related_name="permisos_cuentas_aprobar_fest_2020",blank=True)

    def __str__(self):
        return self.user.email

class Cortes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='cortes_usuario_creacion_fest_2020')
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return self.descripcion


    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')


    def get_valor(self):
        valor = CuentasCobro.objects.filter(corte = self).aggregate(Sum('valor'))['valor__sum']
        return valor if valor != None else 0


    def get_novedades(self):
        cuentas_cobro = CuentasCobro.objects.filter(corte = self, estado__in = ['Creado', 'Cargado'])
        return cuentas_cobro.count()

    def get_cantidad_cuentas_cobro(self):
        return CuentasCobro.objects.filter(corte = self).count()

    def create_cuentas_cobro(self, user):
        objetos = CuposRutaObject.objects.filter(corte = self)
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

def upload_dinamic_cuentas_cobro(instance, filename):
    return '/'.join(['FEST 2020', 'Cuentas de Cobro', str(instance.id), filename])

class CuentasCobro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,related_name='cuentas_cobro_usuario_creacion_fest_2020')

    fecha_actualizacion = models.DateTimeField(blank=True,null=True)
    usuario_actualizacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='usuario_actualizacion_cuentas_cobro_fest_2020')

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

    def get_valor(self):
        return str(self.valor).replace('COL$','')


    def get_consecutivo_corte(self):
        consecutivo = ''
        try:
            consecutivo = self.corte.consecutivo
        except:
            consecutivo = 'Liquidacion'
        return consecutivo

    def get_descripcion_corte(self):
        descripcion = ''
        try:
            descripcion = self.corte.descripcion
        except:
            pass
        return descripcion

    def get_fecha_corte(self):
        fecha = ''
        try:
            fecha = self.corte.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')
        except:
            pass
        return fecha

    def create_delta(self):
        from fest_2020_.functions import delta_cuenta_cobro
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
    return '/'.join(['fest 2020', 'Liquidaciones', str(instance.id), filename])

class Liquidaciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING, blank=True, null=True)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    valor_pagado = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    valor_cancelado = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    transporte_ejecutado = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True, null=True)
    transporte_cancelado = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0, blank=True,null=True)
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

    html = models.FileField(upload_to=upload_dinamic_liquidaciones, blank=True, null=True)
    delta = models.TextField(blank=True, null=True)
    data_json = models.TextField(blank=True, null=True)
    observaciones = models.TextField(default='', blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(blank=True, null=True)
    usuario_actualizacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True,related_name='usuario_actualizacion_liquidacion_2020')

    def __str__(self):
        return self.ruta.nombre


    def pretty_print_valor_pagado(self):
        return str(self.valor_pagado).replace('COL','')

    def pretty_print_valor_cancelado(self):
        return str(self.valor_cancelado).replace('COL','')

    def pretty_print_transporte_ejecutado(self):
        return str(self.transporte_ejecutado).replace('COL','')

    def pretty_print_transporte_cancelado(self):
        return str(self.transporte_cancelado).replace('COL','')

    def get_valor_liquidacion(self):
        valor_liquidacion= float(self.valor_pagado) + float(self.transporte_ejecutado) - float(self.valor_cancelado) - float(self.transporte_cancelado)
        return str(self.valor_liquidacion).replace('COL','')

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


class CuposRutaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creacion = models.DateTimeField(auto_now_add=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='cupo_ruta_fest_2020')
    momento = models.ForeignKey(Momentos,on_delete=models.DO_NOTHING,related_name='cupo_momento_fest_2020', blank=True, null=True)
    estado = models.CharField(max_length=100)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0)
    corte = models.ForeignKey(Cortes, on_delete=models.DO_NOTHING, blank=True, null=True)
    data = JSONField(default=dict)
    liquidacion = models.ForeignKey(Liquidaciones, on_delete=models.DO_NOTHING, blank=True, null=True)

class InstrumentosRutaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='instrumento_usuario_creacion_fest_2020',blank=True,null=True)

    ruta = models.ForeignKey(Rutas, on_delete=models.DO_NOTHING, related_name='instrumento_ruta_fest_2020')
    momento = models.ForeignKey(Momentos, on_delete=models.DO_NOTHING, related_name='instrumento_momento_fest_2020')
    hogares = models.ManyToManyField(Hogares, related_name='instrumento_hogar_fest_2020', blank=True)
    instrumento = models.ForeignKey(Instrumentos, on_delete=models.DO_NOTHING, related_name='instrumento_instrumento_fest_2020',blank=True,null=True)

    modelo = models.CharField(max_length=100)
    soporte = models.UUIDField(blank=True,null=True)
    observacion = models.TextField(blank=True,null=True)
    fecha_actualizacion = models.DateTimeField(blank=True,null=True)
    usuario_actualizacion = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='instrumento_usuario_actualizacion_fest_2020',blank=True,null=True)
    estado = models.CharField(max_length=100,blank=True,null=True)
    nombre = models.CharField(max_length=100,blank=True,null=True)
    consecutivo = models.IntegerField(blank=True,null=True)
    cupo_object = models.ForeignKey(CuposRutaObject,on_delete=models.DO_NOTHING,blank=True,null=True)



    def clean_similares(self):

        from fest_2020_ import modelos_instrumentos

        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)

        if self.instrumento.nivel != 'ruta':

            for instrumento_object in InstrumentosRutaObject.objects.filter(ruta = self.ruta, momento = self.momento, instrumento = self.instrumento).exclude(id = self.id):

                for hogar in self.hogares.all():

                    if hogar in instrumento_object.hogares.all():
                        instrumento_object.hogares.remove(hogar)

                if instrumento_object.hogares.all().count() == 0:
                    self.modelos.get('model').objects.get(id = instrumento_object.soporte).delete()
                    InstrumentosTrazabilidadRutaObject.objects.filter(instrumento = instrumento_object).delete()
                    ObservacionesInstrumentoRutaObject.objects.filter(instrumento = instrumento_object).delete()
                    instrumento_object.delete()
                    self.ruta.update_novedades()



    def get_hogares_list(self):
        hogares = ''

        for hogar in self.hogares.all():
            hogares += '<p>{0} - {1} {2}</p>'.format(hogar.documento,hogar.get_nombres(),hogar.get_apellidos())

        return hogares

    def get_hogares_reporte(self):
        hogares = ''

        for hogar in self.hogares.all():
            hogares += '{0} - {1} {2}\n'.format(hogar.documento,hogar.get_nombres(),hogar.get_apellidos())

        return hogares

class ObservacionesInstrumentoRutaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    instrumento = models.ForeignKey(InstrumentosRutaObject, on_delete=models.DO_NOTHING)
    creacion = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='instrumento_observacion_usuario_creacion_fest_2020',blank=True, null=True)
    observacion = models.TextField(blank=True,null=True)


    def pretty_creation_datetime(self):
        return self.creacion.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

class InstrumentosTrazabilidadRutaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    instrumento = models.ForeignKey(InstrumentosRutaObject,on_delete=models.DO_NOTHING,related_name="trazabilidad_instrumento_fest_2020")
    creacion = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='trazabilidad_instrumento_usuario_fest_2020')
    observacion = models.TextField()



def upload_dinamic_fest(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documento_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documento_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )



    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]








def upload_dinamic_formulario_caracterizacion(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class FormularioCaracterizacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_formulario_caracterizacion_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_formulario_caracterizacion_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_formulario_caracterizacion_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_formulario_caracterizacion,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_formulario_caracterizacion,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]







def upload_dinamic_ficha_icoe(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class FichaIcoe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_ficha_icoe_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_ficha_icoe_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_ficha_icoe',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_ficha_icoe_fest_2020')
    nombre_comunidad = models.CharField(max_length=100)
    resguado_indigena_consejo_comunitario = models.CharField(max_length=100)

    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()


    aspecto_1_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_1_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_1_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_2_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_2_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_2_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_3_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_3_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_3_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_4_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_4_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_4_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    subindice_1_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_1_salida = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_1_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_5_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_5_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_5_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_6_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_6_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_6_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_7_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_7_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_7_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_8_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_8_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_8_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    subindice_2_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_2_salida = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_2_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_9_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_9_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_9_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_10_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_10_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_10_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    aspecto_11_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_11_salida = models.DecimalField(max_digits=10, decimal_places=2)
    aspecto_11_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    subindice_3_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_3_salida = models.DecimalField(max_digits=10, decimal_places=2)
    subindice_3_variacion = models.DecimalField(max_digits=10, decimal_places=2)

    total_entrada = models.DecimalField(max_digits=10, decimal_places=2)
    total_salida = models.DecimalField(max_digits=10, decimal_places=2)
    total_variacion = models.DecimalField(max_digits=10, decimal_places=2)


    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_icoe,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_icoe,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )





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





    def get_extension(self):
        return self.file.name.split('.')[-1]






def upload_dinamic_acta_socializacion_comunidades(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class ActaSocializacionComunidades(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_acta_socializacion_comunidades_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_acta_socializacion_comunidades_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_acta_socializacion_comunidades_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    nombre_comunidad = models.CharField(max_length=100)
    resguado_indigena_consejo_comunitario = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_acta_socializacion_comunidades_fest_2020')
    nombre_representante = models.CharField(max_length=200)
    documento_representante = models.IntegerField()
    cargo_representante = models.CharField(max_length=200)
    fecha_firma = models.DateField()


    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_comunidades,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_comunidades,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_comunidades,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_comunidades,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoSoporteGmail(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class DocumentoSoporteGmail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documento_foto_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento_foto_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documento_foto_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGmail,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGmail,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGmail,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True
    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGmail,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]




def upload_dinamic_DocumentoSoporteAudio(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class DocumentoSoporteAudio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documento_foto_audio_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento_foto_audio_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documento_foto_audio_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoSoporteAudio3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class DocumentoSoporteAudio3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documento_foto_audio3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento_foto_audio3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documento_foto_audio3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=52428800,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_SoporteAudio3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class SoporteAudio3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_foto_audio3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_foto_audio3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_foto_audio3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=52428800,
        max_length=255,
        blank=True,
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=52428800,
        max_length=255,
        blank=True,
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_SoporteAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )
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

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoSoporteGformsFotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporteGformsFotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoportegformsfotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoportegformsfotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoportegformsfotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGmail,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGformsFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGformsFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGformsFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteGformsFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoSoporteFotos2Audio(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporteFotos2Audio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoportefotos2audio_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoportefotos2audio_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoportefotos2audio_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoSoporteFotos2Audio3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporteFotos2Audio3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoportefotos2audio3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoportefotos2audio3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoportefotos2audio3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,

    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoSoporte2Fotos2Audio3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporte2Fotos2Audio3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoporte2fotos2audio3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoporte2fotos2audio3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoporte2fotos2audio3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True,
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True,
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True,
    )

    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True,
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True,
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos2Audio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoSoporteFotosAudio3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporteFotosAudio3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoportefotosaudio3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoportefotosaudio3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoportefotosaudio3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=429916160,
        max_length=255,

    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporteFotosAudio3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoFotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoFotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosfotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosfotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosfotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_DocumentoFotos2Audio(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoFotos2Audio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosfotos2audio_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosfotos2audio_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosfotos2audio_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2Audio,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2Audio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2Audio,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos2Audio,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_Documento2Fotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2Fotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2fotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2fotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2fotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Fotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento2Foto(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2Foto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2foto_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2foto_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2foto_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Foto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Foto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

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


    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoSoporte2Fotos(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporte2Fotos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentossoporte2foto_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentossoporte2foto_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentossoporte2foto_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte2Fotos,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

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

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoFotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoFotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentofoto4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentofoto4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentofoto4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream',
            'application/x-rar-compressed'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url

    def url_file7(self):
        url = None
        try:
            url = self.file7.url
        except:
            pass
        return url

    def url_file8(self):
        url = None
        try:
            url = self.file8.url
        except:
            pass
        return url

    def url_file9(self):
        url = None
        try:
            url = self.file9.url
        except:
            pass
        return url

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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

def upload_dinamic_Documento2soporte(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2Soporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentofoto_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentofoto_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentofoto_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'application/pdf',
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file2.name.split('.')[-1]

def upload_dinamic_Documento2SoporteFotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2SoporteFotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2soportesfotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2soportesfotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2soportesfotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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


    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoSoporte3Fotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporte3Fotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoportes3fotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoportes3fotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoportes3fotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoSoporte3Fotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento3soporte(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3Soporte(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documento3soporte_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento3soporte_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documento3soporte_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'application/pdf',
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True

    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3soporte,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_DocumentoFoto(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DocumentoSoporte2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentosoporte2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentosoporte2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentosoporte2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFoto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFoto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFoto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_DocumentoFoto,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


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

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento2Soporte2Fotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2Soporte2Fotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2soportes2fotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2soportes2fotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2soportes2fotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2Soporte2Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_documento_general(instance, filename):
    return '/'.join(['IRACA', str(instance.ruta.id), str(instance.instrumento.momento.nombre), filename])

class DocumentoGeneral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentogeneral',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentogeneral',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentogeneral',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_general,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=52428800,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_general,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=52428800,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_general,
        content_types=[
            'application/x-rar-compressed',
            'application/octet-stream',
            'application/zip',
            'application/octet-stream',
            'application/x-zip-compressed',
            'multipart/x-zip',
        ],
        max_upload_size=52428800,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_general,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_documento_general,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

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

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_Documento2SoporteFotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2SoporteFotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2soportesfotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2soportesfotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2soportesfotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

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


    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento3SoporteFotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3SoporteFotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos3soportesfotos4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos3soportesfotos4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos3soportesfotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto10 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto11 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto12 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto13 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto14 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto15 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto16 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_foto9(self):
        url = None
        try:
            url = self.foto9.url
        except:
            pass
        return url

    def url_foto10(self):
        url = None
        try:
            url = self.foto10.url
        except:
            pass
        return url

    def url_foto11(self):
        url = None
        try:
            url = self.foto11.url
        except:
            pass
        return url

    def url_foto12(self):
        url = None
        try:
            url = self.foto12.url
        except:
            pass
        return url

    def url_foto13(self):
        url = None
        try:
            url = self.foto13.url
        except:
            pass
        return url

    def url_foto14(self):
        url = None
        try:
            url = self.foto14.url
        except:
            pass
        return url

    def url_foto15(self):
        url = None
        try:
            url = self.foto15.url
        except:
            pass
        return url

    def url_foto16(self):
        url = None
        try:
            url = self.foto16.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file3.name.split('.')[-1]

def upload_dinamic_Documento3SoporteFotos2(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3SoporteFotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos3soportesfotos2_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos3soportesfotos2_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos3soportesfotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'application/pdf',
            'application / vnd.ms - excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos2,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file3.name.split('.')[-1]

def upload_dinamic_Documento3SoporteFotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3SoporteFotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos3soportesfotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos3soportesfotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos3soportesfotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url


    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file3.name.split('.')[-1]

    def get_extension_2(self):
        return self.file5.name.split('.')[-1]

def upload_dinamic_Documento3Soporte2Fotos3Foto(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3Soporte2Fotos3Foto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportes2fotos3foto_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportes2fotos3foto_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportes2fotos3foto_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Soporte2Fotos3Foto,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )



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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file4.name.split('.')[-1]

def upload_dinamic_Documento4SoporteFotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4SoporteFotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportesfotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportesfotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportesfotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg',
            'video/3gpp',

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )
    rar = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream',
            'application/x-rar-compressed',
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def url_rar(self):
        url = None
        try:
            url = self.rar.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file4.name.split('.')[-1]

def upload_dinamic_Documento2SoporteFotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento2SoporteFotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos2soportesfotos4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos2soportesfotos4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos2soportesfotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream',
            'application/x-rar-compressed',
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream',
            'application/x-rar-compressed',
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento2SoporteFotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension_1(self):
        return self.file.name.split('.')[-1]

    def get_extension_2(self):
        return self.file2.name.split('.')[-1]

def upload_dinamic_Documento4SoporteFotos3Fotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4SoporteFotos3Fotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportesfotos3fotos4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportesfotos3fotos4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportesfotos3fotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        null = True,
        blank = True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    file7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    file8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True
    )
    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True

    )
    foto10 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        null=True,
        blank=True

    )
    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url

    def url_file7(self):
        url = None
        try:
            url = self.file7.url
        except:
            pass
        return url

    def url_file8(self):
        url = None
        try:
            url = self.file8.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_foto9(self):
        url = None
        try:
            url = self.foto9.url
        except:
            pass
        return url

    def url_foto10(self):
        url = None
        try:
            url = self.foto10.url
        except:
            pass
        return url

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file7.name.split('.')[-1]

def upload_dinamic_Documento3Fotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento3Fotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos3fotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos3fotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos3fotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento3Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento4Soportes3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4Soportes3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportes3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportes3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportes3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream',
            'application/x-rar-compressed',
            'application/pdf',
        ],
        max_upload_size=859832320,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )


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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_Documento4Soportes4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4Soportes4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportes4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportes4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportes4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Soportes4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos3Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url


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

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension_3(self):
        return self.file3.name.split('.')[-1]

    def get_extension_4(self):
        return self.file4.name.split('.')[-1]


def upload_dinamic_Documento6Fotos3(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento6Fotos3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos6fotos3_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos6fotos3_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos6fotos3_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento6Fotos3,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )


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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_foto9(self):
        url = None
        try:
            url = self.foto9.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file5.name.split('.')[-1]


def upload_dinamic_taller_2_fsc(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class Taller_2_fsc(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='taller_2_fsc_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_taller_2_fsc_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_taller_2_fsc_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255

    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_fsc,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=10485760,
        max_length=255,
        blank = True,
        null = True
    )
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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

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

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_taller_2_sa(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class Taller_2_sa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='taller_2_sa_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_taller_2_sa_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_taller_2_sa_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=10485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_sa,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_taller_2_vmc(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])


class Taller_2_vmc(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='taller_2_vmc_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_taller_2_vmc_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_taller_2_vmc_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'application/x-zip-compressed',
            'application/octet-stream'

        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True

    )
    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=10485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_taller_2_vmc,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url

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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


def upload_dinamic_Documento4SoporteFotos4Fotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4SoporteFotos4Fotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4soportesfotos4fotos4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4soportesfotos4fotos4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4soportesfotos4fotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    file7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    file8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )


    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
                blank=True,
        null=True

    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,

    )
    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,


    )
    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )
    foto9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True

    )

    audio = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4SoporteFotos4Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=429916160,
        max_length=255,
        blank=True,
        null=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url

    def url_file7(self):
        url = None
        try:
            url = self.file7.url
        except:
            pass
        return url

    def url_file8(self):
        url = None
        try:
            url = self.file8.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_foto9(self):
        url = None
        try:
            url = self.foto9.url
        except:
            pass
        return url

    def url_audio(self):
        url = None
        try:
            url = self.audio.url
        except:
            pass
        return url

    def get_extension(self):
        return self.file.name.split('.')[-1]


    def get_extension_1(self):
        return self.file7.name.split('.')[-1]

    def get_extension_2(self):
        return self.file8.name.split('.')[-1]


def upload_dinamic_Documento4Fotos4Fotos4(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4Fotos4Fotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4fotos4fotos4_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4fotos4fotos4_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4fotos4fotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'application/pdf',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos4Fotos4,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )



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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url

    def url_file6(self):
        url = None
        try:
            url = self.file6.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url

    def get_extension_file5(self):
        return self.file5.name.split('.')[-1]

    def get_extension_file6(self):
        return self.file6.name.split('.')[-1]

def upload_dinamic_Documento4Fotos5(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class Documento4Fotos5(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_documentos4fotos5_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documentos4fotos5_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_documentos4fotos5_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )
    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    file5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto7 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto8 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto9 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    audio1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )
    audio3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_Documento4Fotos5,
        content_types=[
            'audio/x-wav',
            'audio/wav',
            'audio/mpeg',
            'audio/x-mpeg',
            'audio/aac',
            'audio/ogg',
            'video/mp4',
            'audio/mp3',
            'audio/x-mp3',
            'video/M4A',
            'video/m4a',
            'audio/mp4',
            'audio/x-mp4',
            'audio/m4a',
            'audio/x-m4a',
            'video/mpeg'
        ],
        max_upload_size=859832320,
        max_length=255,
        null=True,
        blank=True
    )

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

    def url_file4(self):
        url = None
        try:
            url = self.file4.url
        except:
            pass
        return url

    def url_file5(self):
        url = None
        try:
            url = self.file5.url
        except:
            pass
        return url


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url

    def url_foto7(self):
        url = None
        try:
            url = self.foto7.url
        except:
            pass
        return url

    def url_foto8(self):
        url = None
        try:
            url = self.foto8.url
        except:
            pass
        return url

    def url_foto9(self):
        url = None
        try:
            url = self.foto9.url
        except:
            pass
        return url

    def url_audio1(self):
        url = None
        try:
            url = self.audio1.url
        except:
            pass
        return url

    def url_audio2(self):
        url = None
        try:
            url = self.audio2.url
        except:
            pass
        return url

    def url_audio3(self):
        url = None
        try:
            url = self.audio3.url
        except:
            pass
        return url


def upload_dinamic_ficha_vision_desarrollo(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class FichaVisionDesarrollo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_ficha_vision_desarrollo_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_ficha_vision_desarrollo_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_ficha_vision_desarrollo_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_ficha_vision_desarrollo_fest_2020')
    fecha = models.DateField()
    lugar = models.CharField(max_length=100)
    dependencia = models.CharField(max_length=100)

    asistentes = models.IntegerField()


    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_vision_desarrollo,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_vision_desarrollo,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_vision_desarrollo,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_ficha_vision_desarrollo,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]

def upload_dinamic_diagnostico_comunitario(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class DiagnosticoComunitario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_diagnostico_comunitario_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_diagnostico_comunitario_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_diagnostico_comunitario_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_diagnostico_comunitario_fest_2020')
    fecha = models.DateField()
    lugar = models.CharField(max_length=100)
    dependencia = models.CharField(max_length=100)

    asistentes = models.IntegerField()


    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_diagnostico_comunitario,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_diagnostico_comunitario,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_diagnostico_comunitario,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_diagnostico_comunitario,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_diagnostico_comunitario,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]








def upload_dinamic_acta_socializacion_concertacion(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class ActaSocializacionConcertacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_acta_socializacion_concertacion_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_acta_socializacion_concertacion_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_acta_socializacion_concertacion_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)


    fecha_diligenciamiento = models.DateField()
    lugar = models.CharField(max_length=100)
    hora = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_acta_socializacion_concertacion_fest_2020')
    resguado_indigena_consejo_comunitario = models.CharField(max_length=100)
    nombre_comunidad = models.CharField(max_length=100)


    nombre_representante = models.CharField(max_length=200)
    datos_contacto_representante = models.CharField(max_length=200)



    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_concertacion,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_concertacion,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_concertacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_socializacion_concertacion,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
        blank=True,
        null=True
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]







def upload_dinamic_acta_vinculacion_hogar(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class ActaVinculacionHogar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_acta_vinculacion_hogar_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_acta_vinculacion_hogar_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_acta_vinculacion_hogar_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    fecha_diligenciamiento = models.DateField()
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_acta_vinculacion_hogar_fest_2020')
    resguado_indigena_consejo_comunitario = models.CharField(max_length=100)
    nombre_comunidad = models.CharField(max_length=100)

    tipo_identificacion = models.CharField(max_length=100)
    documento_representante = models.IntegerField()
    nombre_representante = models.CharField(max_length=200)
    telefono_celular = models.CharField(max_length=300)


    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_vinculacion_hogar,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    file2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_acta_vinculacion_hogar,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )



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


    def get_extension(self):
        return self.file.name.split('.')[-1]








class DocumentoExcel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_documento_excel_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_documento_excel_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        max_upload_size=50485760,
        max_length=255
    )



    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]


class Fotos4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_fotos4_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_fotos4_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )



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

class Fotos5(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_fotos5_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_fotos5_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url


class Fotos6(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_fotos6_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_fotos6_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )
    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto3 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto4 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto5 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255
    )
    foto6 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )


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

    def url_foto5(self):
        url = None
        try:
            url = self.foto5.url
        except:
            pass
        return url

    def url_foto6(self):
        url = None
        try:
            url = self.foto6.url
        except:
            pass
        return url


class Fotos1(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_fotos1_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_fotos1_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )


    def url_foto1(self):
        url = None
        try:
            url = self.foto1.url
        except:
            pass
        return url




class ArchivoRarZip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_rar_zip_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_rar_zip_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'application/x-rar-compressed',
            'application/zip',
            'application/x-7z-compressed'
        ],
        max_upload_size=50485760,
        max_length=255,
    )


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url



class Fotos2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogar = models.ForeignKey(Hogares,on_delete=models.DO_NOTHING,related_name='hogar_fotos2_fest_2020')
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_fotos2_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    foto1 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )

    foto2 = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_fest,
        content_types=[
            'image/jpg',
            'image/jpeg',
            'image/png'
        ],
        max_upload_size=50485760,
        max_length=255,
    )


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



class Contactos(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, related_name='hcontactos_municipio_fest_2020')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    celular = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    resguardo = models.CharField(max_length=100)
    comunidad = models.CharField(max_length=100)
    lenguas = models.CharField(max_length=100,null=True,blank=True)


    def __str__(self):
        return self.nombres

class Categoria(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    producto = models.IntegerField()

    def __str__(self):
        return self.nombre

class Productos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING, related_name='producto_categoria_fest_2020')
    nombre = models.CharField(max_length=100)
    precio = models.CharField(max_length=100)
    medida=models.CharField(max_length=100)

    def __str__(self):
        return '{0}/{1}  -  ${2}'.format(self.categoria.nombre,self.nombre, self.precio)

def upload_dinamic_huerta_comunitaria(instance, filename):
    return '/'.join(['FEST 2020', str(instance.ruta.id), instance.nombre, filename])

class HuertaComunitaria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hogares = models.ManyToManyField(Hogares,related_name='hogares_huerta_comunitaria_fest_2020',blank=True)
    instrumento = models.ForeignKey(Instrumentos,on_delete=models.DO_NOTHING,related_name='instrumento_huerta_comunitaria_fest_2020',blank=True,null=True)
    ruta = models.ForeignKey(Rutas,on_delete=models.DO_NOTHING,related_name='ruta_huerta_comunitaria_fest_2020',blank=True,null=True)
    nombre = models.CharField(max_length=100)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING,related_name='municipio_huerta_comunitaria_fest_2020')
    fecha = models.DateField()

    producto = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto_huerta_comunitaria_fest_2020')
    cantidad = models.IntegerField(blank=True, null=True)

    producto1 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto1_huerta_comunitaria_fest_2020')
    cantidad1 = models.IntegerField(blank=True, null=True)

    producto2 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto2_huerta_comunitaria_fest_2020')
    cantidad2 = models.IntegerField(blank=True, null=True)

    producto3 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto3_huerta_comunitaria_fest_2020')
    cantidad3 = models.IntegerField(blank=True, null=True)

    producto4 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto4_huerta_comunitaria_fest_2020')
    cantidad4 = models.IntegerField(blank=True, null=True)

    producto5 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto5_huerta_comunitaria_fest_2020')
    cantidad5 = models.IntegerField(blank=True, null=True)

    producto6 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto6_huerta_comunitaria_fest_2020')
    cantidad6 = models.IntegerField(blank=True, null=True)

    producto7 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto7_huerta_comunitaria_fest_2020')
    cantidad7 = models.IntegerField(blank=True, null=True)

    producto8 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto8_huerta_comunitaria_fest_2020')
    cantidad8 = models.IntegerField(blank=True, null=True)

    producto9 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto9_huerta_comunitaria_fest_2020')
    cantidad9 = models.IntegerField(blank=True, null=True)

    producto10 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto10_huerta_comunitaria_fest_2020')
    cantidad10 = models.IntegerField(blank=True, null=True)

    producto11 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto11_huerta_comunitaria_fest_2020')
    cantidad11 = models.IntegerField(blank=True, null=True)

    producto12 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto12_huerta_comunitaria_fest_2020')
    cantidad12 = models.IntegerField(blank=True, null=True)

    producto13 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto13_huerta_comunitaria_fest_2020')
    cantidad13 = models.IntegerField(blank=True, null=True)

    producto14 = models.ForeignKey(Productos, blank=True, null=True, on_delete=models.DO_NOTHING,related_name='producto14_huerta_comunitaria_fest_2020')
    cantidad14 = models.IntegerField(blank=True, null=True)

    valor_total=models.IntegerField(blank=True, null=True)

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_huerta_comunitaria,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]

    @property
    def valor(self):
        precio=Productos.objects.get(self.producto.precio)
        return precio

    def valor1(self):
        precio1=Productos.objects.get(self.producto1.precio)
        return precio1


def upload_dinamic_dir_carga_masiva_hogares(instance, filename):
    return '/'.join(['Carga Masiva Hogares', filename])

class CargaMasivaHogares(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_dir_carga_masiva_hogares, blank=True, null=True)

    def __str__(self):
        return self.nombre




