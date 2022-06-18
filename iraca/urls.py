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


    path('deliverables/', views.DeliverablesOptionsView.as_view()),
    path('deliverables/implementation/', views.VisitsListView.as_view()),
    path('deliverables/implementation/<uuid:pk_moment>/instruments/',views.InstrumentListView.as_view()),
    path('deliverables/implementation/report/', views.ImplementationControlPanel.as_view()),
    path('deliverables/implementation/<uuid:pk_moment>/instruments/report/<uuid:pk_instrument>',views.ImplementationInstrumentReport.as_view()),


    path('deliverables/formulation/', views.FormulationVisitsListView.as_view()),
    path('deliverables/formulation/<uuid:pk_momento>/instruments/',views.FormulationInstrumentListView.as_view()),
    path('deliverables/formulation/report/', views.FormulationControlPanel.as_view()),
    path('deliverables/formulation/<uuid:pk_moment>/instruments/report/<uuid:pk_instrument>',views.FormulationInstrumentReport.as_view()),

    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/', views.MiltoneslistView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/create/', views.MiltonescreateView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/edit/<uuid:pk_milestone>/', views.MilestonesUpdateView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/view/<uuid:pk_milestone>/', views.MilestonesView.as_view()),
    path('certificate/<uuid:pk>/milestones/<uuid:pk_meeting>/delete/<uuid:pk_milestone>/', views.MilestonesDeleteView.as_view()),

    path('certificate/<uuid:pk>/unit/', views.CertificateUnitMiltoneslistView.as_view()),
    path('certificate/<uuid:pk>/unit/create/', views.CertificateUnitMiltonesCreateView.as_view()),
    path('certificate/<uuid:pk>/unit/edit/<uuid:pk_milestone>/', views.CertificateUnitMiltonesUpdateView.as_view()),
    path('certificate/<uuid:pk>/unit/view/<uuid:pk_milestone>/', views.CertificateUnitMiltonesView.as_view()),
    path('certificate/<uuid:pk>/unit/delete/<uuid:pk_milestone>/', views.CertificateUnitMiltonesDeleteView.as_view()),

    path('certificate/<uuid:pk>/resguard/', views.CertificateMunicipiOptionsView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/', views.CertificateResguardOptionsView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/comunity/<uuid:pk_resguard>/', views.CertificateRComunityListView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/comunity/<uuid:pk_resguard>/create/', views.CertificateComunityCreateView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/comunity/<uuid:pk_resguard>/edit/<uuid:pk_milestone>/', views.CertificateComunityUpdateView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/comunity/<uuid:pk_resguard>/view/<uuid:pk_milestone>/', views.CertificateComunityView.as_view()),
    path('certificate/<uuid:pk>/resguard/<uuid:pk_municipity>/comunity/<uuid:pk_resguard>/delete/<uuid:pk_milestone>/', views.CertificateComunityDeleteView.as_view()),


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

    path('supports/', views.SupportsOptionsView.as_view()),
    path('supports/implementation/', views.SupportsHouseholdsImplementationListView.as_view()),
    path('supports/implementation/<uuid:pk_household>/', views.SupportsHouseholdsImplementationMomentsListView.as_view()),
    path('supports/implementation/<uuid:pk_household>/instrument/<uuid:pk_moment>/',views.SupportImplementationHouseholdMomentsListView.as_view()),
    path('supports/implementation/<uuid:pk_household>/instrument/<uuid:pk_moment>/view/<uuid:pk_instrument_object>/',views.SupportHouseholdInstrumentsView.as_view()),

    path('supports/formulation/', views.SupportsHouseholdsFormulationListView.as_view()),
    path('supports/formulation/<uuid:pk_household>/', views.SupportsHouseholdsFormulationMomentsListView.as_view()),
    path('supports/formulation/<uuid:pk_household>/instrument/<uuid:pk_moment>/',views.SupportFormulationHouseholdMomentsListView.as_view()),
    path('supports/formulation/<uuid:pk_household>/instrument/<uuid:pk_moment>/view/<uuid:pk_instrument_object>/',views.FormulationSupportHouseholdInstrumentsView.as_view()),

    path('bonding/', views.HouseholdsListView.as_view()),
    path('bonding/<uuid:pk_household>/', views.BondingListView.as_view()),
    path('bonding/<uuid:pk_household>/view/<uuid:pk_mobile>/', views.BondingView.as_view()),
    path('bonding/<uuid:pk_household>/delete/<uuid:pk_mobile>/', views.BondingDeleteView.as_view()),
    path('bonding/report/', views.HouseholdsReportView.as_view()),
    path('bonding/report_total/', views.HouseholdsReportTotalView.as_view()),

    path('resguard/', views.ResguardListView.as_view()),
    path('resguard/create/', views.ResguardCreateView.as_view()),
    path('resguard/edit/<uuid:pk>/', views.ResguardUpdateView.as_view()),

    path('resguard/comunity/<uuid:pk>/', views.ResguardComunityListView.as_view()),
    path('resguard/comunity/<uuid:pk>/create/', views.ResguardComunityCreateView.as_view()),
    path('resguard/comunity/<uuid:pk>/edit/<uuid:pk_comunity>/', views.ResguardComunityUpdateView.as_view()),


    path('inform/', views.InformListView.as_view()),
    path('inform/view/<uuid:pk_cut>/', views.InformCollectsAccountListView.as_view()),
    path('inform/view/<uuid:pk_cut>/aprobar/<uuid:pk_collect_account>/', views.InformCollectsAccountAprobListView.as_view()),
    path('inform/view/<uuid:pk_cut>/rechazar/<uuid:pk_collect_account>/', views.InformCollectsAccountRejectListView.as_view()),
    path('inform/view/<uuid:pk_cut>/view/<uuid:pk_collect_account>/', views.InformCollectsAccountView.as_view()),
    path('inform/view/<uuid:pk_cut>/report/', views.ReportCollectsAccountListView.as_view()),
    path('inform/view/<uuid:pk_cut>/historial/<uuid:pk_collect_account>/', views.HistorialCollectsAccountView.as_view()),
    path('inform/view/<uuid:pk_cut>/generate/<uuid:pk_collect_account>/', views.InformCollectsAccountgenerateListView.as_view()),

    path('liquidaciones/', views.LiquidacionesListView.as_view()),
    path('liquidaciones/aprobar/<uuid:pk_liquidacion>/', views.LiquidacionesAporbarInforme.as_view()),
    path('liquidaciones/rechazar/<uuid:pk_liquidacion>/', views.LiquidacionesRechazarInforme.as_view()),
    path('liquidaciones/ver/<uuid:pk_liquidacion>/', views.LiquidacionesVerInforme.as_view()),
    path('liquidaciones/historial/<uuid:pk_liquidacion>/', views.LiquidationsHistorialInforme.as_view()),


    path('individual/', views.IndividualOptionsView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/', views.IndividualMunicipioOptionsView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/', views.IndividualMunicipioComunidadListView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/create/', views.IndividualMunicipioComunidadCreateView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/edit/<uuid:pk_ruta>/', views.IndividualMunicipioComunidadupdateView.as_view()),

    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/',views.RutaHogaresListView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/upload/',views.RutaUploadHogaresListView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/',views.RutaHogaresactivitysListView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/',views.RutaHogaresActivitysMomentoListView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/add/<uuid:pk_instrument>/',views.RutaHogaresActivitysMomentoInstrumentCreateView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/view/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/traceability/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentTraceabilityView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/edit/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentObjectView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/delete/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentObjectDeleteView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/aprobe/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentObjectAprobeView.as_view()),
    path('individual/territorio/<uuid:pk_territorio>/resguardo/<uuid:pk_resguardo>/activities/<uuid:pk_ruta>/hogar/<uuid:pk_hogar>/momento/<uuid:pk_momento>/reject/<uuid:pk_instrument_object>/',views.RutaHogaresActivitysMomentoInstrumentObjectRejectView.as_view()),

    path('grupal/', views.GrupalOptionsView.as_view()),
    path('grupal/<uuid:pk>/', views.GrupalListView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/', views.GrupalResguardListView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/create/', views.GrupalResguardCreateView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/edit/<uuid:pk_milestone>/', views.GrupalResguardUpdateView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/view/<uuid:pk_milestone>/', views.GrupalResguardView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/delete/<uuid:pk_milestone>/', views.GrupalResguardDeleteView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/aprobe/<uuid:pk_milestone>/', views.GrupalResguardAprobeView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/reject/<uuid:pk_milestone>/', views.GrupalResguardrejectView.as_view()),
    path('grupal/<uuid:pk>/resguard/<uuid:pk_resguard>/traceability/<uuid:pk_milestone>/', views.GrupalResguardTraceabilityView.as_view()),


]