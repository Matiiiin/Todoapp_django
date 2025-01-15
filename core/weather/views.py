import os
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from django.shortcuts import render
from django.views.generic import TemplateView
import requests
# Create your views here.
class CurrentWeatherDataView(TemplateView):
    template_name = 'weather/current_weather.html'

    @method_decorator(cache_page(60 * 20 , key_prefix='weather'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request , *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        weather_data = requests.get(f'https://api.weatherapi.com/v1/current.json?q=esfahan&key={os.getenv("WEATHERAPI_APIKEY")}')
        data['weather_data'] = weather_data.json()
        return data