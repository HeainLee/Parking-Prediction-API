from django.urls import path
from django.conf import settings

from .views import ParkingModelView

urlpatterns = [
    path('model', ParkingModelView.as_view()),
]
