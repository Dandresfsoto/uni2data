from rest_framework import generics
from rest_framework import mixins
from rest_framework.permissions import AllowAny

from .serializers import FormMobileSerializer, GetFormMobileSerializer
from .models import FormMobile


class FormAPIView(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  generics.GenericAPIView):

    permission_classes = (AllowAny,)
    serializer_class = FormMobileSerializer

    def get_object(self):
        serializer = FormMobileSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return FormMobile.objects.get(id=serializer.data.get("id"))

    def get_queryset(self):
        serializer = GetFormMobileSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        document = serializer.data.get("document")
        queryset = FormMobile.objects.filter(document=document)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = FormMobileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.data.get("id"):
            return self.update(request, *args, **kwargs)
        return self.create(request, *args, **kwargs)
