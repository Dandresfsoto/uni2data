from __future__ import absolute_import, unicode_literals
from config.celery import app
from config.functions import construir_reporte, construir_reporte_pagina
from mail_templated import send_mail
from django.core.files import File

from iraca.models import Moments, Households, Instruments
from iraca.models_instruments import get_model
from mobile.models import FormMobile
from reportes import models as models_reportes


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

    titulos = ['ID hogar', 'Fecha inscripción', 'Departamento de atención', 'Municipio de atención',
               'Codigo municipio de atención', 'Departamento de ubicación', 'Municipio de ubicación', 'Codigo DANE',
               'Zona', 'Codigo zona', 'Corregimiento', 'Vereda/Barrio', 'Localidad/Comuna', 'Barrio', 'Centro poblado',
               'Direccion', 'Ubicacion', 'Numero de telefono', 'Coordenada X', 'Coordenada Y',
               '¿Tiene acceso a otro telefono?', 'Numero adicional 1', 'Numero adicional 2', 'Correo electronico',
               'Acceso a internet', '¿Tiene disponibilidad de tierra?', '¿Tiene disponibilidad de agua?',
               'Tipo de documento', 'ID tipo de documento', 'Parentesco', 'ID Parentesco', '¿Es participante?',
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
               'Servicio publico de acueducto']
    formatos = ['0', 'dd/mm/yyyy', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'dd/mm/yyyy', 'dd/mm/yyyy',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General', 'General',
                'General']
    ancho_columnas = [20, 30, 30, 30, 20, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                      30, 30, 30, 30, 30, 30, 30, 30, 30]
    contenidos = []
    order = []

    mobiles = FormMobile.objects.filter().distinct()
    i = 0

    for mobil in mobiles:
        i += 1
        json_code = mobil.data
        data_members = json_code["members"]
        datas = data_members
        cant = mobil.json_count_document()
        number = 1
        h = 0
        while number <= cant:
            attention_department = json_code["U-20"]
            attention_municipally = json_code["U-21"]
            location_department = json_code["U-1"]
            location_municipally = json_code["U-2"]
            zone = json_code["U-3"]
            township = json_code["U-5"]
            sidewalk = json_code["U-6"]
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
            social_security = household["GE-5"]
            tongue = household["GE-6"]
            id_tongue = ""

            electric_power = json_code["MC-2"]
            public_sewer = json_code["MC-3"]
            gas = "Si"
            trash = json_code["MC-3"]
            aqueduct = json_code["MC-5"]

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
            if count_disabilitys > 1:
                disabilitys = disabilitys[-1]
            else:
                disabilitys = disabilitys[0]

            if disabilitys == "Ver":
                id_disabilitys = "1400"
            elif disabilitys == "Oír":
                id_disabilitys = "1401"
            elif disabilitys == "Hablar":
                id_disabilitys = "1402"
            elif disabilitys == "Moverse o caminar por sí mismo":
                id_disabilitys = "1406"
            elif disabilitys == "Bañarse, vestirse o alimentarse por sí mismo":
                id_disabilitys = "1406"
            elif disabilitys == "Dificultad para salir a la calle sin ayuda o compañía":
                id_disabilitys = "1406"
            elif disabilitys == "Entender o aprender":
                id_disabilitys = "1404"
            elif disabilitys == "Ninguna de las anteriores":
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
                id_comunity = id_comunity
            else:
                id_comunity = "0"

            if ethnic_comunity == "Kumpanía":
                kumpania = id_comunity
            else:
                kumpania = "0"

            if ethnic_comunity == "Kumpanía":
                id_kumpania = id_comunity
            else:
                id_kumpania = "0"

            if ethnic_comunity == " Resguardo":
                guard = id_comunity
            else:
                guard = "0"

            if ethnic_comunity == "Resguardo":
                id_guard = id_comunity
            else:
                id_guard = "0"

            if ethnic_comunity == " Consejo comunitario":
                tip = id_comunity
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
                disabilitys,
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
                ethnic_comunity,
                comunity_other,
                indigenous_people,
                id_comunity,
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
            ]
            contenidos.append(list)

    output = construir_reporte(titulos, contenidos, formatos, ancho_columnas, reporte.nombre, reporte.creation,
                               reporte.usuario, proceso)

    filename = str(reporte.id) + '.xlsx'
    reporte.file.save(filename, File(output))

    return "Reporte generado: " + filename
