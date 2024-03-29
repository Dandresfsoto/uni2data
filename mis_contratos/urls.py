from django.urls import path
from mis_contratos import views

urlpatterns = [
    path('', views.ContratosListView.as_view()),
    path('soportes/<uuid:pk>/', views.ContratosSoportesListView.as_view()),
    path('soportes/<uuid:pk>/editar/<uuid:pk_soporte_contrato>/', views.ContratosSoportesUpdateView.as_view()),

    path('accounts/<uuid:pk>/', views.ContractsAccountsListView.as_view()),
    path('accounts/<uuid:pk>/upload_ss/<uuid:pk_accounts>/', views.ContractsAccountsSegurityUploadView.as_view()),
    path('accounts/<uuid:pk>/upload_account/<uuid:pk_accounts>/', views.ContractsAccountsAccountUploadView.as_view()),
    path('accounts/<uuid:pk>/upload_activity/<uuid:pk_accounts>/', views.ContractsAccountsActivityUploadView.as_view()),
    path('accounts/<uuid:pk>/update_activity/<uuid:pk_accounts>/', views.ContractsAccountsActivityUpdateView.as_view()),
    path('accounts/<uuid:pk>/upload_inform/<uuid:pk_accounts>/', views.ContractsAccountsAccountUploadInformView.as_view()),
]