from __future__ import absolute_import, unicode_literals
from config.celery import app
from config.functions import construir_reporte, construir_reporte_pagina
from mail_templated import send_mail
from django.core.files import File
from django.conf import settings
from pytz import timezone
from datetime import timedelta, datetime

from iraca.models import Moments, Households, Instruments
from iraca.models_instruments import get_model
from mobile.models import FormMobile
from reportes import models as models_reportes

settings_time_zone = timezone(settings.TIME_ZONE)


@app.task
def send_mail_templated_cuenta_cobro(template,dictionary,from_email,list_to_email):
    send_mail(template, dictionary, from_email, list_to_email)
    return 'Email enviado'


@app.task
def build_control_panel_Implementation(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['Consecutivo', 'Cedula', 'Nombre']
    formatos = ['0', 'General', 'General']
    ancho_columnas = [20, 30, 50]
    contenidos = []
    order = []

    for moment in Moments.objects.filter(type_moment="implementacion").order_by('consecutive'):
        order.append(moment)
        titulos.append(f'{moment.name}')
        titulos.append(f'Ruta')
        formatos.append('General')
        formatos.append('General')
        ancho_columnas.append(30)
        ancho_columnas.append(30)

    i = 0

    households = Households.objects.filter().distinct()
    for household in households:
        routes = household.routes.all()
        for route in routes:

            i += 1

            list = [
                i,
                str(household.document),
                str(household.get_full_name())
            ]

            for moment in order:
                list.append(household.get_estate_moment(moment, route))
                list.append(route.name)

            contenidos.append(list)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename


@app.task
def build_control_panel_Formulation(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['Consecutivo', 'Cedula', 'Nombre']
    formatos = ['0', 'General', 'General']
    ancho_columnas = [20, 30, 50]
    contenidos = []
    order = []

    for moment in Moments.objects.filter(type_moment="formulacion").order_by('consecutive'):
        order.append(moment)
        titulos.append(f'{moment.name}')
        titulos.append(f'Ruta')
        formatos.append('General')
        formatos.append('General')
        ancho_columnas.append(30)
        ancho_columnas.append(30)

    i = 0

    households = Households.objects.filter().distinct()
    for household in households:
        routes = household.routes.all()
        for route in routes:

            i += 1

            list = [
                i,
                str(household.document),
                str(household.get_full_name())
            ]

            for moment in order:
                list.append(household.get_estate_moment(moment, route))
                list.append(route.name)

            contenidos.append(list)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename


@app.task
def build_report_instrument(id, instrument_id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    instrument = Instruments.objects.get(id=instrument_id)
    model = get_model(instrument.model)['model']
    proceso = "SICAN-IRACA 2021"
    order = []
    titulos = []
    formatos = []
    ancho_columnas = []
    contenidos = []

    for field in model._meta.get_fields():
        order.append(field.name)
        titulos.append(field.verbose_name)
        formatos.append('General')
        ancho_columnas.append(30)

    for data in model.objects.filter(instrument=instrument):
        lista = []
        for name in order:
            obj = getattr(data, name)

            if name == 'households':
                value = ''
                for household in obj.all():
                    value += str(household.document) + ', '

                lista.append(value[:-2])
            else:
                lista.append(str(obj))
        contenidos.append(lista)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename


@app.task
def build_bonding_report(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['ID persona','ID hogar', 'Fecha inscripción', 'Departamento de atención', 'Municipio de atención',
               'Codigo municipio de atención', 'Departamento de ubicación', 'Municipio de ubicación', 'Codigo DANE',
               'Zona', 'Codigo zona', 'Corregimiento', 'Vereda/Barrio','ID Vereda/Barrio','Otras veredas', 'Localidad/Comuna', 'Barrio', 'Centro poblado',
               'Direccion', 'Ubicacion', 'Numero de telefono', 'Coordenada X', 'Coordenada Y',
               '¿Tiene acceso a otro telefono?', 'Numero adicional 1', 'Numero adicional 2', 'Correo electronico',
               'Acceso a internet', '¿Tiene disponibilidad de tierra?', '¿Tiene disponibilidad de agua?',
               'Tipo de documento', 'ID tipo de documento','Numero de documento', 'Parentesco', 'ID Parentesco', '¿Es participante?',
               'Primer nombre', 'Segundo nombre', 'Primer apellido', 'Segundo apellido', 'Sexo', 'Id Sexo', 'Genero',
               'Id Genero', 'Condicion sexual', 'ID Condicion sexual', 'Fecha nacimiento', 'Fecha expedicion documento',
               'Estado Civil', 'ID Estado Civil', 'Etnia', 'ID Etnia', 'Tipos de discapacidad', 'ID Discapacidad',
               '¿Sabe leer y escribir?', '¿Sabe sumar y restar?', 'Nivel educativo alcanzado',
               'ID Nivel educativo alcanzado', '¿Actualmente estudia?', 'Razon no estudia', 'ID Razon no estudia',
               'Otra razon', '¿Recibe alimentos?', 'Regímen de seguridad', 'ID Regímen de seguridad', 'Grupo etnico',
               'ID Grupo etnico', 'Comunidad etnica', '¿Cual?', 'Pueblo indigena', 'ID Pueblo indigena',
               'Comunidad étnica', 'ID comunidad étnica', 'Resguardo etnico', 'ID resguardo etnico',
               'Consejo comunitario', 'ID Consejo comunitario', '¿Se comunican a través de una lengua nativa?',
               'Indique el nombre de la lengua por la cual se comunica', 'ID lengua',
               'servicio publico de energia electrica', 'Servicio publico de Alcantarillado',
               'Servicio publico de gas natural domiciliario', 'Servicio publico de recolección de basuras',
               'Servicio publico de acueducto','Gestor profesional']
    formatos = ['0','0', 'dd/mm/yyyy', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'dd/mm/yyyy', 'dd/mm/yyyy',
                'General', 'dd/mm/yyyy', 'dd/mm/yyyy', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General','General','General','General','General']
    ancho_columnas = [20,20, 30, 30, 30, 20, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
    contenidos = []
    order = []

    mobiles = FormMobile.objects.filter().distinct()
    i = 0
    j = 0
    for mobil in mobiles:
        i += 1
        json_code = mobil.data
        data_members = json_code["members"]
        datas = data_members
        cant = mobil.json_count_document()
        professional = mobil.document
        number = 1
        h = 0
        while number <= cant:
            j += 1
            attention_department = json_code["U-20"]
            attention_municipally = json_code["U-21"]
            location_department = json_code["U-1"]
            location_municipally = json_code["U-2"]
            zone = json_code["U-3"]
            township = json_code["U-5"]
            sidewalk = json_code["U-6"]
            id_sidewalk = ""
            other_sidewalk = ""
            location = json_code["U-4"]
            neighborhood = json_code["U-7"]
            populated_center = json_code["U-8"]
            direction = json_code["U-9"]
            location = json_code["U-9"]
            phone = json_code["U-12"]
            x = json_code["lon"]
            y = json_code["lat"]
            other_phone = json_code["U-13"]
            ethernet = json_code["U-17"]
            earth = json_code["U-18"]
            water = json_code["U-18"]
            household = datas[h]
            type_document = household["CG-1"]
            id_type = ""
            number_document = household["CG-2"]
            relationship = household["CG-11"]
            id_relationship = ""
            partaker = ""
            first_name = household["CG-3"]
            second_name = household["CG-4"]
            first_surname = household["CG-5"]
            second_surname = household["CG-6"]
            sex = household["CG-7"]
            id_sex = ""
            gender = household["CG-8"]
            id_gender = ""
            sexual_condition = household["CG-9"]
            id_sexual_condition = ""
            date_init = household["CG-10"]
            date_exp = ""
            marital_status = household["CG-12"]
            id_marital_status = ""
            ethnicity = json_code["GE-1"]
            id_ethnicity = ""
            disabilitys = household["CG-13"]
            id_disabilitys = ""
            type_document = household["CG-1"]
            read = household["ES-1"]
            sum = household["ES-2"]
            education_level = household["ES-3"]
            id_education_level = ""
            education = household["ES-4"]
            not_education = "0"
            id_not_education = "0"
            other_not_education = "0"
            educational_food = household["ES-5"]
            social_security = household["ES-6"]
            id_social_security = ""
            ethnic_group = json_code["GE-1"]
            id_ethnic_group = ""
            ethnic_comunity = json_code["GE-2"]
            comunity = json_code["GE-4"]
            id_comunity = json_code["GE-3"]
            indigenous_people = ""
            comunity_other = "0"
            guard = ""
            tip = ""
            social_security = household["ES-6"]
            tongue = household["GE-6"]
            id_tongue = ""

            electric_power = json_code["MC-2"]
            public_sewer = json_code["MC-3"]
            gas = "Si"
            trash = json_code["MC-3"]
            aqueduct = json_code["MC-5"]

            date_init = datetime.strptime(date_init,'%Y/%m/%d')

            if date_exp == "":
                date_exp = date_init + timedelta((365*18)+(365/12))
            else:
                date_exp = datetime.strptime(date_exp, '%Y/%m/%d')



            if type_document == "Cédula de Ciudadanía (CC)":
                id_type = "153"
            elif type_document == "Tarjeta de identidad (TI)":
                id_type = "154"
            elif type_document == "Cédula de extranjería (CE)":
                id_type = "155"
            elif type_document == "Registro Civil (RC)":
                id_type = "156"
            elif type_document == "No tiene":
                id_type = "158"
            elif type_document == "Pasaporte (PAS)":
                id_type = "163"
            elif type_document == "Documento Nacional de Identidad (DNI)":
                id_type = "850"
            elif type_document == "Documento Nacional de Identidad (DNI)":
                id_type = "850"
            elif type_document == "Salvoconducto para refugiados (SAL)":
                id_type = "851"
            elif type_document == "Permiso especial de permanencia (PEP)":
                id_type = "852"

            if relationship == "Jefe del hogar":
                id_relationship = "673"
            elif relationship == "Cónyuge o compañero(a)":
                id_relationship = "674"
            elif relationship == "Hijo(a) o hijastro(a) o hijo(a) adoptivo":
                id_relationship = "675"
            elif relationship == "Yerno / Nuera":
                id_relationship = "676"
            elif relationship == "Nieto(a)":
                id_relationship = "677"
            elif relationship == "Padre, madre, padrastro, madrastra":
                id_relationship = "678"
            elif relationship == "Suegro (a)":
                id_relationship = "679"
            elif relationship == "Hermano(a)":
                id_relationship = "680"
            elif relationship == "Otro pariente":
                id_relationship = "681"
            elif relationship == "Abuelo (a)":
                id_relationship = "686"
            elif relationship == "Tío(a)":
                id_relationship = "687"
            elif relationship == "Sobrino(a)":
                id_relationship = "688"
            elif relationship == "Primo(a)":
                id_relationship = "689"
            elif relationship == "Otro no pariente":
                id_relationship = "690"
            elif relationship == "Cuñado(a)":
                id_relationship = "691"
            elif relationship == "NO REPORTA":
                id_relationship = "1226"
            elif relationship == "Empleado del servicio doméstico":
                id_relationship = "3001"
            elif relationship == "Pariente del servicio doméstico":
                id_relationship = "3002"
            elif relationship == "Pensionista":
                id_relationship = "3003"
            elif relationship == "Pariente de pensionista":
                id_relationship = "3004"

            if relationship == "Jefe del hogar":
                partaker = "SI"
            else:
                partaker = "NO"

            if sex == "Mujer":
                id_sex = "7"
            elif sex == "Hombre":
                id_sex = "8"
            elif sex == "Intersexual":
                id_sex = "137"

            if sexual_condition == "":
                id_sexual_condition = "0"
            elif sexual_condition == "Bisexual":
                id_sexual_condition = "621"
            elif sexual_condition == "Gay":
                id_sexual_condition = "622"
            elif sexual_condition == "Lesbiana":
                id_sexual_condition = "623"
            elif sexual_condition == "Heterosexual":
                id_sexual_condition = "624"
            elif sexual_condition == "No responde":
                id_sexual_condition = "625"

            if gender == "":
                id_gender = "0"
            elif gender == "Masculino":
                id_gender = "615"
            elif gender == "Femenino":
                id_gender = "616"
            elif gender == "Transgenero":
                id_gender = "617"

            if marital_status == "":
                id_marital_status = "0"
            elif marital_status == "Casado(a)":
                id_marital_status = "265"
            elif marital_status == "Soltero(a)":
                id_marital_status = "266"
            elif marital_status == "Viudo(a)":
                id_marital_status = "316"
            elif marital_status == "Unión libre":
                id_marital_status = "317"
            elif marital_status == "Separado(a) o divorciado(a)":
                id_marital_status = "318"

            if ethnicity == "":
                id_ethnicity = "0"
            elif ethnicity == "Rom o Gitano(a)":
                id_ethnicity = "10"
            elif ethnicity == "Ninguno de las anteriores":
                id_ethnicity = "11"
            elif ethnicity == "Indígena":
                id_ethnicity = "12"
            elif ethnicity == "Negro(a), mulato(a), afrodescendiente, afrocolombiano(a)":
                id_ethnicity = "40"
            elif ethnicity == "Palenquero(a) de San Basilio":
                id_ethnicity = "41"
            elif ethnicity == "Raizal del Archipielago de San Andrés, Providencia y Santa Catalina":
                id_ethnicity = "9"

            count_disabilitys = len(disabilitys)
            if count_disabilitys == 0:
                disabilitys_end = "Ninguna de las anteriores"
            else:
                disabilitys_end = disabilitys[0]

            if disabilitys_end == "Ver":
                id_disabilitys = "1400"
            elif disabilitys_end == "Oír":
                id_disabilitys = "1401"
            elif disabilitys_end == "Hablar":
                id_disabilitys = "1402"
            elif disabilitys_end == "Moverse o caminar por sí mismo":
                id_disabilitys = "1406"
            elif disabilitys_end == "Bañarse, vestirse o alimentarse por sí mismo":
                id_disabilitys = "1406"
            elif disabilitys_end == "Dificultad para salir a la calle sin ayuda o compañía":
                id_disabilitys = "1406"
            elif disabilitys_end == "Entender o aprender":
                id_disabilitys = "1404"
            elif disabilitys_end == "Ninguna de las anteriores":
                id_disabilitys = "0"

            if education_level == "Ninguno":
                id_education_level = "84"
            elif education_level == "Preescolar":
                id_education_level = "85"
            elif id_education_level == "Básica primaria (1°. - 5°.)":
                id_education_level = "86"
            elif education_level == "Básica Secundaria (6° - 9°)":
                id_education_level = "87"
            elif education_level == "Media (10° - 13°)":
                id_education_level = "88"
            elif education_level == "Técnico o tecnológico (1-4)":
                id_education_level = "98"
            elif education_level == "Universitario (1-6)":
                id_education_level = "100"
            elif education_level == "Posgrado (1-4)":
                id_education_level = "83"

            if social_security == "Contributivo (EPS)":
                id_social_security = "1540"
            elif social_security == "Especial (Fuerzas Armadas, Ecopetrol, universidades públicas, magisterio)":
                id_social_security = "1541"
            elif social_security == "Subsidiado (EPS-S)":
                id_social_security = "1542"
            elif social_security == "EPS indígena":
                id_social_security = "1543"
            elif social_security == "Ninguna":
                id_social_security = "1544"
            elif social_security == "No sabe":
                id_social_security = "1545"

            if ethnic_group == "Rom o Gitano(a)":
                id_ethnic_group = "10"
            elif ethnic_group == "Ninguno de las anteriores":
                id_ethnic_group = "11"
            elif ethnic_group == "Indígena":
                id_ethnic_group = "12"
            elif ethnic_group == "Negro(a), mulato(a), afrodescendiente, afrocolombiano(a)":
                id_ethnic_group = "40"
            elif ethnic_group == "Palenquero(a) de San Basilio":
                id_ethnic_group = "41"
            elif ethnic_group == "Raizal del Archipielago de San Andrés, Providencia y Santa Catalina":
                id_ethnic_group = "9"

            if ethnic_comunity == "Pueblo indígena":
                indigenous_people = comunity
            else:
                indigenous_people = "0"



            if ethnic_comunity == "Pueblo indígena":
                id_indigenous_people = id_comunity
            else:
                id_indigenous_people = "0"

            if ethnic_comunity == "Kumpanía":
                kumpania = comunity
            else:
                kumpania = "0"

            if ethnic_comunity == "Kumpanía":
                id_kumpania = id_comunity
            else:
                id_kumpania = "0"

            if ethnic_comunity == "Resguardo":
                guard = comunity
            else:
                guard = "0"

            if ethnic_comunity == "Resguardo":
                id_guard = id_comunity
            else:
                id_guard = "0"

            if ethnic_comunity == "Consejo comunitario":
                tip = comunity
            else:
                tip = "0"

            if ethnic_comunity == "Consejo comunitario":
                id_tip = id_comunity
            else:
                id_tip = "0"

            electric_count = 0
            electricity = ""
            for electric in electric_power:
                if electric == "Si":
                    electric_count += 1

            if electric_count > 0:
                electricity = "Si"
            else:
                electricity = "No"

            sewer = ""
            if public_sewer == "Ninguno":
                sewer = "No"
            else:
                sewer = "Si"

            public_trash = ""
            if trash == "La recogen los servicios de aseo":
                public_trash = "Si"
            else:
                public_trash = "No"

            public_aqueduct = ""
            if aqueduct == "Acueducto":
                public_aqueduct = "Si"
            else:
                public_aqueduct = "No"

            h += 1
            number += 1
            list = [
                j,
                i,
                mobil.pretty_creation_datetime(),
                attention_department,
                attention_municipally,
                mobil.json_attention_municipally_cod(),
                location_department,
                location_municipally,
                mobil.json_location_municipally_cod(),
                zone,
                mobil.json_zone_cod(),
                township,
                sidewalk,
                id_sidewalk,
                other_sidewalk,
                location,
                neighborhood,
                populated_center,
                direction,
                location,
                phone,
                x,
                y,
                other_phone,
                mobil.json_other_phone(),
                mobil.json_other_phone_2(),
                mobil.json_email(),
                ethernet,
                earth[0],
                water[1],
                type_document,
                id_type,
                number_document,
                relationship,
                id_relationship,
                partaker,
                first_name,
                second_name,
                first_surname,
                second_surname,
                sex,
                id_sex,
                gender,
                id_gender,
                sexual_condition,
                id_sexual_condition,
                date_init,
                date_exp,
                marital_status,
                id_marital_status,
                ethnicity,
                id_ethnicity,
                disabilitys_end,
                id_disabilitys,
                read,
                sum,
                education_level,
                id_education_level,
                education,
                not_education,
                id_not_education,
                other_not_education,
                educational_food,
                social_security,
                id_social_security,
                ethnic_group,
                id_ethnic_group,
                ethnic_comunity, #Comunidad etnica
                comunity_other,
                indigenous_people,
                id_indigenous_people,
                kumpania,
                id_kumpania,
                guard,
                id_guard,
                tip,
                id_tip,
                social_security,
                tongue,
                id_tongue,
                electricity,
                sewer,
                gas,
                public_trash,
                public_aqueduct,
                professional,
            ]
            contenidos.append(list)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename

@app.task
def build_bonding_total_report(id):
    reporte = models_reportes.Reportes.objects.get(id=id)
    proceso = "IRACA 2021"

    titulos = ['ID persona','ID hogar','Fecha inscripción','Departamento de ubicación','Municipio de ubicación','Zona',
               'Localidad o comuna','Corregimiento','Vereda','Barrio','Centro poblado','Direccion','Coordenada X',
               'Coordenada Y','Numero de telefono','¿Otro telefono?','Telefono adicional 1','Telefono adicional 2',
               'Email','¿Acceso intenet?','¿Tierra?','¿Agua?','Codigo departamento atencion','Nombre departamento atencion',
               'Codigo municipio atencion','Nombre municipio atencion','Codigo del proyecto','Fecha registro presupuestal',
               'Estado beneficiario','Tipo de documento','Numero de documento','Primer nombre','Segundo nombre',
               'Primer apellido','Segundo apellido','Sexo','Genero','Orientacion sexual','Fecha de nacimiento','Parentesco',
               'Estado civil','Limitantes','¿Sabe leer y escribir?','¿Sabe sumar y restar?','Nivel educativo',
               '¿Actualmente estudia?','¿Recibe... en el plantel educativo alimento','Regimen seguridad social','Proyecto productivo',
               '¿Razon no activo?','La unidad productiva es','Bienes o servicios','3 principales bienes o servicios',
               '3 variedades bienes o servicios','Tiempo funcionando','¿Tiene RUT?','¿Camara de comercio?','¿Cuantos empleados?',
               '¿Servicios publicos del proyecto?','¿Cuenta con parcela?','¿Cuenta con maquinaria?','¿Cuenta con herramientas?',
               '¿Cuenta con infraestructura?','¿Cuenta con insumos?','¿Cuenta con animales?','¿Cuenta con establecimiento?',
               '¿Selecciona el producto 1?','¿Lava el producto 1?','¿Empaca el producto 1?','¿Almacena el producto 1?',
               '¿Transforma el producto 1?','¿Selecciona el producto 2?','¿Lava el producto 2?','¿Empaca el producto 2?',
               '¿Almacena el producto 2?','¿Transforma el producto 2?','¿Selecciona el producto 3?','¿Lava el producto 3?',
               '¿Empaca el producto 3?','¿Almacena el producto 3?','¿Transforma el producto 3?','¿Su proyecto cuenta con Invima?',
               '¿Su proyecto cuenta con sellos de calidad?','¿Su proyecto cuenta con sellos de certificaciones de valor agregado?',
               '¿Su proyecto cuenta con certificacion de manipulacion?', '¿Su proyecto cuenta con cursos de formacion?',
               '¿Su proyecto cuenta con codigo de barras?','¿Cuanto volumen produce para le venta mensual del producto 1?',
               '¿Cuanto volumen produce para le venta mensual del producto 2?','¿Cuanto volumen produce para le venta mensual del producto 3?',
               'Promedio mensual de ventas','Promedio de las ganancias mensuales','¿Cubre el mercado veredal?','¿Cubre el mercado municipal?',
               '¿Cubre el mercado departamental?','¿Cubre el mercado regional?','¿Cubre el mercado nacional?','¿Cubre el mercado internacional?',
               '¿Comercializa su producto a traves de intermediario particular?','¿Comercializa su producto a traves de mayorista?',
               '¿Comercializa su producto a traves de plaza de mercado?','¿Comercializa su producto a traves de mmercado campesino?',
               '¿Comercializa su producto a traves de consumidor final?','¿Comercializa su producto a traves de plataform de comercio electronico?',
               '¿Comercializa su producto a traves de agroindustria?', '¿Comercializa su producto a traves de almacen de cadena?',
               '¿Comercializa su producto a traves de exportador?', '¿Comercializa su producto a traves de compras publicas?',
               '¿Comercializa su producto a traves de organizacion de productores?','¿Comercializa su producto a traves de trueque?',
               '¿Cuenta con algún lugar para almacenar o guardar provisiones','¿para su venta el producto requiere que este sea trasladado?',
               '¿Utiliza redes sociales para vender su producto?','¿Lleva un registro de costos, ingresos y gastos?',
               '¿Cuál es la razón principal para no llevar este registro?','¿Cómo maneja los residuos sólidos y líquidos?',
               '¿Durante el último año, ha recibido apoyo en los siguientes aspecto: Financiamiento?',
               '¿Durante el último año, ha recibido apoyo en los siguientes aspecto: Capacitacion?',
               '¿Durante el último año, ha recibido apoyo en los siguientes aspecto: Provision de tierra?',
               '¿Durante el último año, ha recibido apoyo en los siguientes aspecto: Provision de insumos?',
               '¿Requiere apoyo para fortalecer su proyecto: Financiamiento?','¿requiere apoyo para fortalecer su proyecto: Capacitacion?',
               '¿Requiere apoyo para fortalecer su proyecto: Acceso a tierra?',
               '¿Requiere apoyo para fortalecer su proyecto: Asistencia tecnica?','¿Requiere apoyo para fortalecer su proyecto: Insumos?',
               '¿Requiere apoyo para fortalecer su proyecto: Compra de activos?','¿Requiere apoyo para fortalecer su proyecto: Certificaciones sanitarias?',
               '¿Requiere apoyo para fortalecer su proyecto: Apoyo para la comercializacion?','¿Requiere apoyo para fortalecer su proyecto: Formalizacion?',
               '¿Requiere apoyo para fortalecer su proyecto: Registro de marca?','¿Requiere apoyo para fortalecer su proyecto: Facturacion?',
               '¿Requiere apoyo para fortalecer su proyecto: Transporte?','¿Requiere apoyo para fortalecer su proyecto: acceso a Internet?',
               '¿Usted pertenece a alguna organización productiva?','¿Le gustaría pertenecer a alguna organización productiva?',
               '¿Cuál es la razón principal para no pertenecer?','¿Qué tipo de organización es?','Nombre completo de la organización',
               '¿La organización productiva a la que pertenece está legalmente constituida?','NIT de la organización',
               '¿Cuál es el nombre completo del representante legal de la organización?','¿Cuál es el número de celular de la organización?',
               '¿El hogar lleva un presupuesto?','¿tiene y utiliza cuenta ahorro o corriente?','¿tiene y utiliza cuenta dinero movil?',
               '¿tiene y utiliza tarjeta de credito?','¿tiene y utiliza seguro de accidentes?','¿tiene y utiliza seguro agropecuario?',
               '¿En cuál de las siguientes entidades bancarias tiene su cuenta de ahorros o corriente?', '¿Produce actualmente alimentos?',
               '¿Produce actualmente hortalizas?','¿Produce actualmente aromaticas?','¿Produce actualmente frutales de ciclo corto?',
               '¿Produce actualmente musaceas?','¿Produce actualmente leguminosas?','¿Produce actualmente tuberculos?','¿Produce actualmente frutales de tardio rendimiento?',
               '¿Produce actualmente cereales?','¿Produce actualmente carne de ave?','¿Produce actualmente carne de chivo?',
               '¿Produce actualmente carne de cuy?','¿Produce actualmente carne de cerdo?','¿Produce actualmente leche o derivados?',
               '¿Produce actualmente huevos?','¿Produce actualmente pesca?','¿Produce actualmente alimentos silvestres?',
               '¿Cuáles son las principales razones para no hacerlo?','¿Usa abono organico para el terreno?',
               '¿Usa abono quimico para el terreno?','¿Usa abono mixto para el terreno?','¿No usa abono para el terreno?',
               '¿Qué tipo de método utiliza para el manejo de plaga en cultivos?','¿Qué tipo de método utiliza para el manejo de plaga en animales?',
               '¿Qué tipo de semilla usa principalmente?','¿Cuenta con tanque para el riego?','¿Qué utiliza para la alimentación de los animales?',
               '¿Qué hace con los excedentes de su producción de autoconsumo?','¿Cuánto dinero recibe por los excedentes?',
               '¿Dónde vende los excedentes?','¿Lavo/seco los excedentes?','¿Empaco los excedentes?','¿Prceso los excedentes?',
               '¿Cuánto dinero estima que se ahorra en un mes?','¿Cuántos metros cuadrados mide el espacio de terreno?',
               '¿Algún integrante del hogar se ha preocupado por no tener suficientes alimentos?',
               '¿Algún integrante del hogar se ha preocupado por no haya podido comer alimentos sano?',
               '¿Algún integrante del hogar se ha preocupado por que haya comido poca variedad de alimentos?',
               '¿Algún integrante del hogar se ha preocupado por que haya tenido que saltarse una comida?',
               '¿Algún integrante del hogar se ha preocupado por que haya comido menos de lo que pensaba que debía comer?',
               '¿Algún integrante del hogar se ha preocupado por que su hogar se haya quedado sin alimentos?',
               '¿Algún integrante del hogar se ha preocupado por que haya sentido hambre pero no comió?',
               '¿Algún integrante del hogar se ha preocupado por que haya dejado de comer durante todo un día?',
               '¿Su hogar pertenece a alguno de los siguientes grupos étnicos?','¿Usted habita en algunas de estas comunidades étnicas?',
               'Código pueblo indígena / territorio colectivo / comunidad étnica','Indique el nombre de la comunidad étnica',
               '¿Se comunican a través de una lengua nativa?','Indique el nombre de la lengua por la cual se comunica',
               'Inundaciones','Avalanchas','Terremotos','Incendios','Vendavales','Hundimientos','Plagas',
               '¿Su comunidad cuenta con interconexión eléctrica?','¿Su comunidad cuenta con energia solar?',
               '¿Su comunidad cuenta con planta electrica a gasolina?','¿Con cuál servicio de alcantarillado cuenta la comunidad?',
               '¿Cómo eliminan principalmente la basura?','El agua se obtiene de...','¿En el plantel educativo se brindan alimentos',
               '¿El plantel educativo imparte educación que respeta y desarrolla la identidad cultural de su pueblo?']
    formatos = ['0','0','dd/mm/yyyy','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','dd/mm/yyyy','General','General','General',
                'General','General','General','General','General','General','General','dd/mm/yyyy','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General','General','General',
                'General','General','General','General','General','General','General','General''General','General',
                'General''General','General','General','General','General','General','General']
    ancho_columnas = [20,20,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,
                      30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
    contenidos = []
    order = []

    mobiles = FormMobile.objects.filter().distinct()
    i = 0
    j = 0
    for mobil in mobiles:
        i += 1
        json_code = mobil.data
        data_members = json_code["members"]
        datas = data_members
        cant = mobil.json_count_document()
        professional = mobil.document
        number = 1
        h = 0
        while number <= cant:
            j += 1
            household = datas[h]

            location_department = json_code["U-1"]
            location_municipally = json_code["U-2"]
            zone = json_code["U-3"]
            location = json_code["U-4"]
            township = json_code["U-5"]
            sidewalk = json_code["U-6"]
            neighborhood = json_code["U-7"]
            populated_center = json_code["U-8"]
            direction = json_code["U-9"]
            x = json_code["lon"]
            y = json_code["lat"]
            phone = json_code["U-12"]
            other_phone = json_code["U-13"]
            ethernet = json_code["U-17"]
            earth = json_code["U-18"]
            water = json_code["U-18"]
            departament_atencion_id = json_code["U-19"]
            departament_atencion_name = json_code["U-20"]
            municipality_atencion_id = json_code["U-21"]
            municipality_atencion_name = json_code["U-22"]
            id_proyect = json_code["U-24"]
            date_register_budget = json_code["U-25"]
            beneficiary_estate = json_code["U-26"]
            type_document = household["CG-1"]
            number_document = household["CG-2"]
            first_name = household["CG-3"]
            second_name = household["CG-4"]
            first_surname = household["CG-5"]
            second_surname = household["CG-6"]
            sex = household["CG-7"]
            gender = household["CG-8"]
            sexual_condition = household["CG-9"]
            date_init = household["CG-10"]
            relationship = household["CG-11"]
            marital_status = household["CG-12"]
            limiting = household["CG-13"]
            text_limit = ",".join(limiting)
            read = household["ES-1"]
            sum = household["ES-2"]
            education_level = household["ES-3"]
            education = household["ES-4"]
            educational_food = household["ES-5"]
            social_security = household["ES-6"]
            productive_project = json_code["PP-3"]
            reason_no_active = json_code["PP-4"]
            productive_unit = json_code["PP-5"]
            good_or_services = json_code["PP-8"]
            text_good_or_services = ",".join(good_or_services)
            principal_good_or_services = json_code["PP-9"]
            text_principal_good_or_services = ",".join(principal_good_or_services)
            main_varieties = json_code["PP-10"]
            text_main_varieties = ",".join(main_varieties)
            function_time = json_code["PP-11"]
            rut = json_code["PP-12"]
            commerce = json_code["PP-13"]
            emnployees = json_code["PP-15"]
            public_services = json_code["PP-21"]
            text_public_services = ",".join(public_services)
            actives = json_code["PP-22"]
            aggregate = json_code["PP-23"]
            registers = json_code["PP-24"]
            volume = json_code["PP-26"]
            monthly_average_sales = json_code["PP-27"]
            monthly_average_profit = json_code["PP-29"]
            market_coverage = json_code["PP-30"]
            markets_through = json_code["PP-31"]
            warehouse = json_code["PP-32"]
            transfer = json_code["PP-34"]
            social_networks = json_code["PP-35"]
            cost_record = json_code["PP-36"]
            not_cost_record = json_code["PP-37"]
            wasted_solid_and_liquid = json_code["PP-38"]
            support_last_year = json_code["PP-39"]
            strengthen_project = json_code["PP-41"]
            productive_organization = json_code["A-1"]
            productive_organization_option = json_code["A-2"]
            reason_not_productive_organization = json_code["A-3"]
            type_productive_organization = json_code["A-4"]
            full_name_productive_organization = json_code["A-5"]
            legal_productive_organization = json_code["A-6"]
            nit_productive_organization = json_code["A-7"]
            represent_productive_organization = json_code["A-8"]
            mobil_productive_organization = json_code["A-9"]
            budget = json_code["IEF-1"]
            financial_instruments = json_code["IEF-2"]
            bank_account = json_code["IEF-3"]
            food = json_code["AU-1"]
            food_variety = json_code["AU-2"]
            not_food_variety = json_code["AU-3"]
            fertilizer = json_code["AU-8"]
            plant_plage = json_code["AU-9"]
            animals_plage = json_code["AU-10"]
            seed = json_code["AU-12"]
            irrigation_tanks = json_code["AU-13"]
            animal_feed = json_code["AU-14"]
            surplus = json_code["AU-15"]
            surplus_money = json_code["AU-16"]
            surplus_sale = json_code["AU-17"]
            surplus_add = json_code["AU-18"]
            save_money = json_code["AU-19"]
            space = json_code["AU-20"]
            food_safety = json_code["SA-1"]
            ethnic_group = json_code["GE-1"]
            ethnic_comunity = json_code["GE-2"]
            id_comunity = json_code["GE-3"]
            comunity = json_code["GE-4"]
            tongue_options = household["GE-5"]
            tongue = household["GE-6"]
            catastrophe = json_code["MC-1"]
            electric_power = json_code["MC-2"]
            sewerage = json_code["MC-3"]
            crash = json_code["MC-4"]
            water_public = json_code["MC-5"]
            educative_food = json_code["MC-6"]
            Etnoeducation = json_code["MC-7"]

            h += 1
            number += 1
            list = [
                j,
                i,
                mobil.pretty_creation_datetime(),
                location_department,
                location_municipally,
                zone,
                location,
                township,
                sidewalk,
                neighborhood,
                populated_center,
                direction,
                x,
                y,
                phone,
                other_phone,
                mobil.json_other_phone(),
                mobil.json_other_phone_2(),
                mobil.json_email(),
                ethernet,
                earth[0],
                water[1],
                departament_atencion_id,
                departament_atencion_name,
                municipality_atencion_id,
                municipality_atencion_name,
                id_proyect,
                date_register_budget,
                beneficiary_estate,
                type_document,
                number_document,
                first_name,
                second_name,
                first_surname,
                second_surname,
                sex,
                gender,
                sexual_condition,
                date_init,
                relationship,
                marital_status,
                text_limit,
                read,
                sum,
                education_level,
                education,
                educational_food,
                social_security,
                productive_project,
                reason_no_active,
                productive_unit,
                text_good_or_services,
                text_principal_good_or_services,
                text_main_varieties,
                function_time,
                rut,
                commerce,
                emnployees,
                text_public_services,
                actives[0],
                actives[1],
                actives[2],
                actives[3],
                actives[4],
                actives[5],
                actives[6],
                aggregate[0],
                aggregate[1],
                aggregate[2],
                aggregate[3],
                aggregate[4],
                aggregate[5],
                aggregate[6],
                aggregate[7],
                aggregate[8],
                aggregate[9],
                aggregate[10],
                aggregate[11],
                aggregate[12],
                aggregate[13],
                aggregate[14],
                registers[0],
                registers[1],
                registers[2],
                registers[3],
                registers[4],
                registers[5],
                volume[0],
                volume[1],
                volume[2],
                monthly_average_sales,
                monthly_average_profit,
                market_coverage[0],
                market_coverage[1],
                market_coverage[2],
                market_coverage[3],
                market_coverage[4],
                market_coverage[5],
                markets_through[0],
                markets_through[1],
                markets_through[2],
                markets_through[3],
                markets_through[4],
                markets_through[5],
                markets_through[6],
                markets_through[7],
                markets_through[8],
                markets_through[9],
                markets_through[10],
                markets_through[11],
                warehouse,
                transfer,
                social_networks,
                cost_record,
                not_cost_record,
                wasted_solid_and_liquid,
                support_last_year[0],
                support_last_year[1],
                support_last_year[2],
                support_last_year[3],
                strengthen_project[0],
                strengthen_project[1],
                strengthen_project[2],
                strengthen_project[3],
                strengthen_project[4],
                strengthen_project[5],
                strengthen_project[6],
                strengthen_project[7],
                strengthen_project[8],
                strengthen_project[9],
                strengthen_project[10],
                strengthen_project[11],
                strengthen_project[12],
                productive_organization,
                productive_organization_option,
                reason_not_productive_organization,
                type_productive_organization,
                full_name_productive_organization,
                legal_productive_organization,
                nit_productive_organization,
                represent_productive_organization,
                mobil_productive_organization,
                budget,
                financial_instruments[0],
                financial_instruments[1],
                financial_instruments[2],
                financial_instruments[3],
                financial_instruments[4],
                bank_account,
                food,
                food_variety[0],
                food_variety[1],
                food_variety[2],
                food_variety[3],
                food_variety[4],
                food_variety[5],
                food_variety[6],
                food_variety[7],
                food_variety[8],
                food_variety[9],
                food_variety[10],
                food_variety[11],
                food_variety[12],
                food_variety[13],
                food_variety[14],
                food_variety[15],
                not_food_variety,
                fertilizer[0],
                fertilizer[1],
                fertilizer[2],
                fertilizer[3],
                plant_plage,
                animals_plage,
                seed,
                irrigation_tanks,
                animal_feed,
                surplus,
                surplus_money,
                surplus_sale,
                surplus_add[0],
                surplus_add[1],
                surplus_add[2],
                save_money,
                space,
                food_safety[0],
                food_safety[1],
                food_safety[2],
                food_safety[3],
                food_safety[4],
                food_safety[5],
                food_safety[6],
                food_safety[7],
                ethnic_group,
                ethnic_comunity,
                id_comunity,
                comunity,
                tongue_options,
                tongue,
                catastrophe[0],
                catastrophe[1],
                catastrophe[2],
                catastrophe[3],
                catastrophe[4],
                catastrophe[5],
                catastrophe[6],
                electric_power[0],
                electric_power[1],
                electric_power[2],
                sewerage,
                crash,
                water_public,
                educative_food,
                Etnoeducation,
            ]
            contenidos.append(list)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename

@app.task
def build_list_collects_account(id, id_cuts):
    from recursos_humanos.models import Cuts, Collects_Account
    reporte = models_reportes.Reportes.objects.get(id=id)
    cuts = Cuts.objects.get(id = id_cuts)
    proceso = "SICAN-LIST-CUENTAS DE COBRO"


    titulos = ['Consecutivo', 'Código','Proyecto', 'Cargo' ,'Contratista', 'Cédula', 'Valor total contrato','Seguridad social','informe de actividades','Reporte']

    formatos = ['0', 'General','General', 'General', 'General', '0', '"$"#,##0_);("$"#,##0)','0','0','0']

    ancho_columnas = [20, 30, 30, 30, 40,25, 35, 40, 20, 40, 40, 40]

    contenidos = []
    order = []


    i = 0
    for collect_account in Collects_Account.objects.filter(cut=id_cuts):
        i += 1


        lista = [
            int(i),
            collect_account.contract.nombre,
            collect_account.contract.get_proyecto(),
            collect_account.contract.get_cargo(),
            collect_account.contract.contratista.get_full_name(),
            collect_account.contract.contratista.cedula,
            collect_account.contract.valor.amount,
            collect_account.estate,
            collect_account.estate_inform,
            collect_account.estate_report,
        ]

        contenidos.append(lista)


    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation, reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))


    return "Archivo paquete ID: " + filename
