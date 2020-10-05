from django.urls import path
from django.conf import settings

from .views import ParkingModelView
from .views import BatchModelView

urlpatterns = [
    path('model', ParkingModelView.as_view()),
    path('batch', BatchModelView.as_view()),
]
