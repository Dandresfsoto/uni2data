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

    path('certificate/<uuid:pk>/unit/', rest_views.MilestonesUnitListApi.as_view()),

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

    path('resguard/', rest_views.ResguardListApi.as_view()),

    path('resguard/comunity/<uuid:pk>/', rest_views.ResguardComunityListApi.as_view()),

    path('inform/', rest_views.InformListApi.as_view()),
    path('inform/view/<uuid:pk_cut>/', rest_views.InformCollectAccountListApi.as_view()),

    path('liquidaciones/', rest_views.LiquidacionesListApi.as_view()),

    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/', rest_views.IndividualMunicipioComunidadListApi.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/', rest_views.IndividualMunicipioComunidadHogaresListApi.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/', rest_views.IndividualMunicipioComunidadHogaresActivitysListApi.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/', rest_views.IndividualMunicipioComunidadHogaresActivitysMomentoListApi.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/traceability/<uuid:pk_instrument_object>/', rest_views.IndividualMunicipioComunidadHogaresActivitysMomentoTrazabilidadListApi.as_view()),

    path('grupal/<uuid:pk>/', rest_views.GrupalListApi.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/', rest_views.GrupaResguardlListApi.as_view()),
]