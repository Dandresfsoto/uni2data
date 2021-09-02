from django.urls import path, include
from iraca import rest_views

urlpatterns = [
    path('certificate/<uuid:pk>/', rest_views.MeetingsListApi.as_view()),

    path('certificate/autocomplete/municipios/', rest_views.MunicipiosAutocomplete.as_view()),
]