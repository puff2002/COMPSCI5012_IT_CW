from django.urls import path

from .views import ConfigView, WeatherNowView, WeatherSearchView

urlpatterns = [
    path("config/", ConfigView.as_view(), name="config"),
    path("weather/search/", WeatherSearchView.as_view(), name="weather-search"),
    path("weather/now/", WeatherNowView.as_view(), name="weather-now"),
]
