from rest_framework import serializers
from .models import FormMobile


class GetFormMobileSerializer(serializers.Serializer):
    document = serializers.IntegerField()


class FormMobileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = FormMobile
        fields = "__all__"
        read_only = ["id"]
