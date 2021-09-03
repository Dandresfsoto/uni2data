from django.urls import path, include
from iraca import views

urlpatterns = [
    path('', views.IracaOptionsView.as_view()),


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

]