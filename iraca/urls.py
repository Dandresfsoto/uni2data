from django.urls import path, include
from iraca import views

urlpatterns = [
    path('', views.IracaOptionsView.as_view()),

    path('bd/', views.HogaresListView.as_view()),
    path('bd/crear/', views.HogaresCreateView.as_view()),
    path('bd/edit/<uuid:pk>/', views.HogaresUpdateView.as_view()),

    path('certificate/', views.CerticateOptionsView.as_view()),
    path('certificate/<uuid:pk>/', views.CerticateListView.as_view()),
    path('certificate/<uuid:pk>/create/', views.CerticateCreateView.as_view()),

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

]