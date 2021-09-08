from django.urls import path, include
from iraca import views

urlpatterns = [
    path('', views.IracaOptionsView.as_view()),

    path('bd/', views.HouseholdListView.as_view()),
    path('bd/create/', views.HouseholdCreateView.as_view()),
    path('bd/edit/<uuid:pk>/', views.HouseholdUpdateView.as_view()),

    path('certificate/', views.CerticateOptionsView.as_view()),
    path('certificate/<uuid:pk>/', views.CerticateListView.as_view()),
    path('certificate/<uuid:pk>/create/', views.CerticateCreateView.as_view()),

    path('deliverables/', views.VisitsListView.as_view()),
    path('deliverables/<uuid:pk_momento>/instruments/',views.InstrumentListView.as_view()),

    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/', views.MiltoneslistView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/create/', views.MiltonescreateView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/edit/<uuid:pk_milestone>/', views.MilestonesUpdateView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/view/<uuid:pk_milestone>/', views.MilestonesView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/delete/<uuid:pk_milestone>/', views.MilestonesDeleteView.as_view()),

    path('certificate/<uuid:pk>/contacts/<uuid:pk_meeting>/', views.ContactslistView.as_view()),
    path('certificate/<uuid:pk>/contacts/<uuid:pk_meeting>/create/', views.ContactsCreateView.as_view()),
    path('certificate/<uuid:pk>/contacts/<uuid:pk_meeting>/edit/<uuid:pk_contact>/', views.ContactsUpdateView.as_view()),

    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/estate/<uuid:pk_milestone>/', views.MilestonesEstateUpdateView.as_view()),

    path('socialization/', views.SocializationOptionsView.as_view()),
    path('socialization/<uuid:pk>/', views.SocializationListView.as_view()),
    path('socialization/<uuid:pk>/create/', views.SocializationCreateView.as_view()),


    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/', views.SocializationMiltoneslistView.as_view()),
    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/create/', views.SocializationMiltonescreateView.as_view()),
    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/edit/<uuid:pk_milestone>/', views.SocializationMilestonesUpdateView.as_view()),
    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/view/<uuid:pk_milestone>/', views.SocializationMilestonesView.as_view()),
    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/delete/<uuid:pk_milestone>/', views.SocializationMilestonesDeleteView.as_view()),

    path('socialization/<uuid:pk>/milestones/<uuid:pk_meeting>/estate/<uuid:pk_milestone>/',views.SocializationMilestonesEstateUpdateView.as_view()),

    path('socialization/<uuid:pk>/contacts/<uuid:pk_meeting>/', views.SocializationContactslistView.as_view()),
    path('socialization/<uuid:pk>/contacts/<uuid:pk_meeting>/create/', views.SocializationContactsCreateView.as_view()),
    path('socialization/<uuid:pk>/contacts/<uuid:pk_meeting>/edit/<uuid:pk_contact>/', views.SocializationContactsUpdateView.as_view()),


    path('implementation/', views.ImplementationListView.as_view()),
    path('implementation/create/', views.ImplementationCreateView.as_view()),
    path('implementation/edit/<uuid:pk>/', views.ImplementationUpdateView.as_view()),
    path('implementation/activities/<uuid:pk>/', views.ImplementationActivitiesListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/', views.ImplementationHouseholdsListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/add/<uuid:pk_instrument>/', views.ImplementationInstrumentsListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/view/<uuid:pk_instrument_object>/', views.ImplementationInstrumentsObjectListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/household/<uuid:pk_instrument_object>/', views.ImplementationHouseholdsObjectListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/traceability/<uuid:pk_instrument_object>/', views.ImplementationTraceabilityObjectListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/edit/<uuid:pk_instrument_object>/', views.ImplementationUpdateObjectListView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/approve/<uuid:pk_instrument_object>/', views.ApproveInstrumentHouseholdView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/reject/<uuid:pk_instrument_object>/', views.RejectInstrumentHouseholdView.as_view()),
    path('implementation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/delete/<uuid:pk_instrument_object>/', views.DeleteInstrumentHouseholdView.as_view()),

    path('implementation/household/<uuid:pk>/', views.ImplementationHouseholdListView.as_view()),
    path('implementation/household/<uuid:pk>/view/<uuid:pk_household>', views.ImplementationHouseholdView.as_view()),


    path('formulation/', views.FormulationListView.as_view()),
    path('formulation/activities/<uuid:pk>/', views.FormulationActivitiesListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/',views.FormulationHouseholdsListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/add/<uuid:pk_instrument>/',views.FormulationInstrumentsListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/view/<uuid:pk_instrument_object>/',views.FormulationInstrumentsObjectListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/household/<uuid:pk_instrument_object>/',views.FormulationHouseholdsObjectListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/traceability/<uuid:pk_instrument_object>/', views.FormulationTraceabilityObjectListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/edit/<uuid:pk_instrument_object>/',views.FormulationUpdateObjectListView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/approve/<uuid:pk_instrument_object>/',views.FormulationApproveInstrumentHouseholdView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/reject/<uuid:pk_instrument_object>/',views.FormulationRejectInstrumentHouseholdView.as_view()),
    path('formulation/activities/<uuid:pk>/instruments/<uuid:pk_moment>/delete/<uuid:pk_instrument_object>/',views.FormulationDeleteInstrumentHouseholdView.as_view()),

    path('formulation/household/<uuid:pk>/', views.FormulationHouseholdListView.as_view()),
    path('formulation/household/<uuid:pk>/view/<uuid:pk_household>', views.FormulationtionHouseholdView.as_view()),
]