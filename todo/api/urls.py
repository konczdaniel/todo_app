from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_weather),  # Matches /weather/?city=London
]