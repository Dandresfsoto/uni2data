from django.urls import path
from mobile import rest_views

urlpatterns = [
    path('forms/', rest_views.FormAPIView.as_view()),
]
