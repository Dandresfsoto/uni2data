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
