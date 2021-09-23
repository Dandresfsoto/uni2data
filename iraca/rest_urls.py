from django.urls import path, include
from iraca import rest_views

urlpatterns = [

    path('bd/', rest_views.HogaresListApi.as_view()),

    path('deliverables/implementation/', rest_views.MomentsListApi.as_view()),
    path('deliverables/implementation/<uuid:pk_moment>/instruments/',rest_views.InstrumentsListApi.as_view()),

    path('deliverables/formulation/', rest_views.FormulationMomentsListApi.as_view()),
    path('deliverables/formulation/<uuid:pk_moment>/instruments/',rest_views.FormulationInstrumentsListApi.as_view()),

    path('certificate/<uuid:pk>/', rest_views.MeetingsListApi.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/', rest_views.MilestonesListApi.as_view()),

    path('certificate/<uuid:pk>/contacts/<uuid:pk_meeting>/', rest_views.ContactsListApi.as_view()),

    path('implementation/', rest_views.ImplementationListApi.as_view()),
    path('implementation/activities/<uuid:pk>/', rest_views.ImplementationActivitiesListApi.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/', rest_views.ImplementationHouseholdListApi.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/traceability/<uuid:pk_instrument_object>/', rest_views.ImplementationTraceabilityListApi.as_view()),

    path('implementation/household/<uuid:pk>/', rest_views.ImplementationHouseholdsListApi.as_view()),

    path('certificate/autocomplete/municipios/', rest_views.MunicipiosAutocomplete.as_view()),

    path('formulation/', rest_views.FormulationListApi.as_view()),
    path('formulation/activities/<uuid:pk>/', rest_views.FormulationActivitiesListApi.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/',rest_views.FormulationHouseholdListApi.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/traceability/<uuid:pk_instrument_object>/',rest_views.FormulationTraceabilityListApi.as_view()),

    path('formulation/household/<uuid:pk>/', rest_views.FormulationHouseholdsListApi.as_view()),


    path('supports/implementation/', rest_views.SupportsHouseholdsListApi.as_view()),
    path('supports/implementation/<uuid:pk_household>/', rest_views.SupportsHouseholdsImplementationMomentsListApi.as_view()),
    path('supports/implementation/<uuid:pk_household>/instrument/<uuid:pk_moment>/',rest_views.SupportImplementationHouseholdMomentsListApi.as_view()),

    path('supports/formulation/', rest_views.SupportsFormulationHouseholdsListApi.as_view()),
    path('supports/formulation/<uuid:pk_household>/', rest_views.SupportsHouseholdsFormulationMomentsListApi.as_view()),
    path('supports/formulation/<uuid:pk_household>/instrument/<uuid:pk_moment>/',rest_views.SupportFormulationHouseholdMomentsListApi.as_view()),

    path('bonding/', rest_views.HouseholdListApi.as_view()),
    path('bonding/<uuid:pk_household>/', rest_views.BondingListApi.as_view()),
]