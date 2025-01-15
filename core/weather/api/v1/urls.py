from django.urls import path
from . import views
urlpatterns = [
    path('current' , views.CurrentWeatherAPIView.as_view() , name='current-weather')
]