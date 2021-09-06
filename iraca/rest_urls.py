from django.urls import path, include
from iraca import rest_views

urlpatterns = [

    path('bd/', rest_views.HogaresListApi.as_view()),

    path('deliverables/', rest_views.MomentsListApi.as_view()),
    path('deliverables/<uuid:pk_moment>/instruments/',rest_views.InstrumentsListApi.as_view()),

    path('certificate/<uuid:pk>/', rest_views.MeetingsListApi.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/', rest_views.MilestonesListApi.as_view()),

    path('certificate/<uuid:pk>/contacts/<uuid:pk_meeting>/', rest_views.ContactsListApi.as_view()),

    path('implementation/', rest_views.ImplementationListApi.as_view()),

    path('certificate/autocomplete/municipios/', rest_views.MunicipiosAutocomplete.as_view()),
]