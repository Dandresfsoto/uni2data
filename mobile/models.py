import json
import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField


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


