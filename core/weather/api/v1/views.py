from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import os
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CurrentWeatherAPIView(APIView):
    @method_decorator(cache_page(60 * 20))
    def get(self ,request):
        weather_data = requests.get(f'https://api.weatherapi.com/v1/current.json?q=esfahan&key={os.getenv("WEATHERAPI_APIKEY")}')
        return Response(weather_data.json())