from django.contrib import admin

from iraca import models

admin.site.register(models.Certificates)
admin.site.register(models.Meetings)
admin.site.register(models.Types)
admin.site.register(models.Milestones)