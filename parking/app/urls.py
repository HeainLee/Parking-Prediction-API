from django.urls import path
from django.conf import settings

from .views import ParkingModelView, ParkingModelDetailView

urlpatterns = [
    path('model', ParkingModelView.as_view()),
    path('model/<pk>', ParkingModelDetailView.as_view()),
]
