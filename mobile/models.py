import json
import uuid
from pytz import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField

from django.conf import settings

settings_time_zone = timezone(settings.TIME_ZONE)

class FormMobile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    document = models.BigIntegerField()
    data = JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document}"

    def json_read_document(self):
        json_code = self.data
        data_members = json_code["members"]
        documents = data_members[0]
        document = documents["CG-2"]
        return str(document)

    def json_read_name(self):
        json_code = self.data
        data_members = json_code["members"]
        documents = data_members[0]
        document = str(documents["CG-3"] + " " + documents["CG-5"])
        return str(document)

    def json_read_earth(self):
        json_code = self.data
        data_disponibility = json_code["U-18"]
        earth = data_disponibility[0]
        return str(earth)

    def json_read_water(self):
        json_code = self.data
        data_disponibility = json_code["U-18"]
        water = data_disponibility[1]
        return str(water)

    def json_read_members_boss(self):
        json_code = self.data
        data_disponibility = json_code["members"]
        boss = data_disponibility[0]
        return boss

    def pretty_creation_datetime(self):
        return self.created_at.astimezone(settings_time_zone).strftime('%d/%m/%Y')

    def json_attention_municipally_cod(self):
        json_code = self.data
        data_members = json_code["U-21"]
        if data_members == "EL LITORAL DEL SAN JUAN":
            return str("27250")
        elif data_members == "RIOSUCIO":
            return str("27615")
        elif data_members == "CARMEN DE DARIEN":
            return str("27150")
        elif data_members == "UNGUIA":
            return str("27800")
        elif data_members == "ACANDI":
            return str("27006")
        elif data_members == "ALTO BAUDO":
            return str("27025")
        elif data_members == "ALTO BAUDO":
            return str("27077")
        elif data_members == "ALTO BAUDO":
            return str("27099")
        elif data_members == "ATRATO":
            return str("27050")
        elif data_members == "RIO QUITO":
            return str("27600")

    def json_location_municipally_cod(self):
        json_code = self.data
        data_members = json_code["U-2"]
        if data_members == "EL LITORAL DEL SAN JUAN":
            return str("27250")
        elif data_members == "RIOSUCIO":
            return str("27615")
        elif data_members == "CARMEN DE DARIEN":
            return str("27150")
        elif data_members == "UNGUIA":
            return str("27800")
        elif data_members == "ACANDI":
            return str("27006")
        elif data_members == "ALTO BAUDO":
            return str("27025")
        elif data_members == "ALTO BAUDO":
            return str("27077")
        elif data_members == "ALTO BAUDO":
            return str("27099")
        elif data_members == "ATRATO":
            return str("27050")
        elif data_members == "RIO QUITO":
            return str("27600")

    def json_zone_cod(self):
        json_code = self.data
        data_members = json_code["U-3"]
        if data_members == "Cabecera municipal":
            return str("1")
        elif data_members == "Centro poblado":
            return str("2")
        elif data_members == "Rural disperso":
            return str("3")

    def json_other_phone(self):
        json_code = self.data
        data_members = json_code["U-14"]
        if data_members == "":
            return str("0")
        else:
            return str(data_members)

    def json_other_phone_2(self):
        json_code = self.data
        data_members = json_code["U-15"]
        if data_members == "":
            return str("0")
        else:
            return str(data_members)

    def json_email(self):
        json_code = self.data
        data_members = json_code["U-16"]
        if data_members == "":
            return str("0")
        elif data_members == "no aplica ":
            return str("0")
        else:
            return str(data_members)

    def json_count_document(self):
        json_code = self.data
        data_members = json_code["members"]
        cant = len(data_members)
        return cant



