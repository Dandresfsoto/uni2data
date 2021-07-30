from django.urls import path
from formatos import views

urlpatterns = [
    path('', views.ComponentesView.as_view()),
    path('crear/', views.ComponentesLevel1CreateView.as_view()),
    path('editar/<uuid:pk>/', views.ComponentesLevel1UpdateView.as_view()),

    path('<uuid:pk>/', views.ComponentesLevel2View.as_view()),
    path('<uuid:pk>/crear/', views.ComponentesLevel2CreateView.as_view()),
    path('<uuid:pk>/editar/<uuid:pk_l2>/', views.ComponentesLevel2UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/', views.ComponentesLevel3View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/crear/', views.ComponentesLevel3CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/editar/<uuid:pk_l3>/', views.ComponentesLevel3UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/', views.ComponentesLevel4View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/crear/', views.ComponentesLevel4CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/editar/<uuid:pk_l4>/', views.ComponentesLevel4UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/', views.ComponentesLevel5View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/crear/', views.ComponentesLevel5CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/editar/<uuid:pk_l5>/', views.ComponentesLevel5UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/', views.ComponentesLevel6View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/crear/', views.ComponentesLevel6CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/editar/<uuid:pk_l6>/', views.ComponentesLevel6UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/', views.ComponentesLevel7View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/crear/', views.ComponentesLevel7CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/editar/<uuid:pk_l7>/', views.ComponentesLevel7UpdateView.as_view()),

    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/<uuid:pk_l7>/', views.ComponentesLevel8View.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/<uuid:pk_l7>/crear/', views.ComponentesLevel8CreateView.as_view()),
    path('<uuid:pk>/<uuid:pk_l2>/<uuid:pk_l3>/<uuid:pk_l4>/<uuid:pk_l5>/<uuid:pk_l6>/<uuid:pk_l7>/editar/<uuid:pk_l8>/', views.ComponentesLevel8UpdateView.as_view()),
]