from django.urls import path , include
from . import views
urlpatterns = [
    path('current/',views.CurrentWeatherDataView.as_view() , name='current-weather'),
    path('api/v1/' , include('weather.api.v1.urls'))
]