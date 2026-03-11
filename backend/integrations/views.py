from asgiref.sync import async_to_sync
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.weather import get_weather, search_city
from storage.config_store import get_masked_config, update_config


class ConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(get_masked_config())

    def post(self, request):
        config = update_config(
            api_base=request.data.get("api_base"),
            api_key=request.data.get("api_key"),
            model=request.data.get("model"),
            removebg_api_key=request.data.get("removebg_api_key"),
            bg_removal_method=request.data.get("bg_removal_method"),
        )
        if hasattr(config, "model_dump"):
            data = config.model_dump()
        else:
            data = config.dict()
        return Response({"message": "updated", **data})


class WeatherSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("query")
        if not query:
            return Response({"detail": "query required"}, status=status.HTTP_400_BAD_REQUEST)
        cities = async_to_sync(search_city)(query)
        payload = []
        for city in cities:
            if hasattr(city, "model_dump"):
                payload.append(city.model_dump())
            else:
                payload.append(city.dict())
        return Response(payload)


class WeatherNowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        location = request.query_params.get("location")
        if not location:
            return Response({"detail": "location required"}, status=status.HTTP_400_BAD_REQUEST)
        weather = async_to_sync(get_weather)(location)
        if not weather:
            return Response({"detail": "weather unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if hasattr(weather, "model_dump"):
            return Response(weather.model_dump())
        return Response(weather.dict())
