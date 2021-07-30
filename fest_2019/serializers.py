from rest_framework import serializers
from .models import ProyectosApi, GeoreferenciacionApi
from usuarios.models import User


class GeoreferenciacionApiSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeoreferenciacionApi
        fields = ['id','json']
        read_only_fields = ['id']


    def create(self, validated_data):

        if validated_data['json']['data']['isSynchronized'] == False:
            validated_data['json']['data']['isSynchronized'] = True

        try:
            documento_gestor = validated_data['json']['documento']
        except:
            instance = GeoreferenciacionApi.objects.create(**validated_data)
        else:
            if 'document' in validated_data['json']['data'].keys():
                query = GeoreferenciacionApi.objects.filter(json__documento=documento_gestor,json__data__document = validated_data['json']['data']['document'])
            else:
                query = GeoreferenciacionApi.objects.filter(json__documento=documento_gestor,json__data__code = validated_data['json']['data']['code'])
            if query.count() > 0:
                query.update(**validated_data)
                instance = query[0]
            else:
                instance = GeoreferenciacionApi.objects.create(**validated_data)

        return instance


class ProyectosApiSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProyectosApi
        fields = ['id','json']
        read_only_fields = ['id']


    def validate_json(self, validated_data):
        try:
            documento_gestor = validated_data['json']['documento']
            codigo_proyecto = validated_data['json']['data']['projectCode']

        except:
            pass
        else:

            query = ProyectosApi.objects.filter(json__documento=documento_gestor, json__data__projectCode=codigo_proyecto)
            if query.count() > 0:

                for proyecto in query:
                    if not proyecto.actualizar_app:
                        raise serializers.ValidationError("El proyecto no permite ser actualizado")



        return validated_data



    def create(self, validated_data):

        if validated_data['json']['data']['isSynchronized'] == False:
            validated_data['json']['data']['isSynchronized'] = True

        try:
            documento_gestor = validated_data['json']['documento']
            codigo_proyecto = validated_data['json']['data']['projectCode']

        except:
            try:
                user = User.objects.get(cedula=documento_gestor)
            except:
                user = None

            instance = ProyectosApi.objects.create(**validated_data)
            instance.agregar_observacion(user=user, estado = "Cargado", descripcion="Proyecto creado")
        else:

            try:
                user = User.objects.get(cedula=documento_gestor)
            except:
                user = None

            query = ProyectosApi.objects.filter(json__documento=documento_gestor, json__data__projectCode=codigo_proyecto)
            if query.count() > 0:

                copiado = False

                for proyecto in query:
                    proyecto.agregar_observacion(user=user, estado="Actualización", descripcion="Proyecto actualizado")

                    instance = proyecto
                    instance.json = validated_data['json']
                    instance.save()


            else:
                instance = ProyectosApi.objects.create(**validated_data)
                instance.agregar_observacion(user=user, estado="Cargado", descripcion="Proyecto creado")
        return instance
