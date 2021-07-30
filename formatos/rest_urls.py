from django.urls import path
from formatos import rest_views

urlpatterns = [
    path('', rest_views.Level1ListApi.as_view()),
    path('<uuid:pk_l1>/', rest_views.Level2ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/', rest_views.Level3ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/<uuid:pk_l3>/', rest_views.Level4ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/', rest_views.Level5ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/', rest_views.Level6ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/', rest_views.Level7ListApi.as_view()),
    path('<uuid:pk_l1>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/<uuid:pk_l7>/', rest_views.Level8ListApi.as_view()),
]