import random

from asgiref.sync import async_to_sync
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from services.recommendation import get_llm_recommendation
from services.weather import get_season_from_weather, get_weather
from wardrobe.models import ClothingItem

from .models import Outfit, OutfitHistory, WeatherSnapshot
from .serializers import OutfitHistorySerializer, OutfitSerializer


def _weather_to_raw(weather):
    if hasattr(weather, "model_dump"):
        return weather.model_dump()
    if hasattr(weather, "dict"):
        return weather.dict()
    return {}


class OutfitHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = OutfitHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OutfitHistory.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        location = request.data.get("location")
        if not location:
            return Response({"detail": "location required"}, status=status.HTTP_400_BAD_REQUEST)

        weather = async_to_sync(get_weather)(location)
        if not weather:
            return Response({"detail": "weather unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        seasons = get_season_from_weather(weather)
        items = list(ClothingItem.objects.filter(owner=request.user))

        def is_suitable(item):
            return any(season in (item.season_semantics or []) for season in seasons)

        tops = [item for item in items if item.category == "top" and is_suitable(item)]
        bottoms = [item for item in items if item.category == "bottom" and is_suitable(item)]

        if not tops:
            tops = [item for item in items if item.category == "top"]
        if not bottoms:
            bottoms = [item for item in items if item.category == "bottom"]

        suggested_top = random.choice(tops) if tops else None
        suggested_bottom = random.choice(bottoms) if bottoms else None

        recommendation_text = async_to_sync(get_llm_recommendation)(
            weather,
            seasons,
            tops,
            bottoms,
        )

        weather_snapshot = WeatherSnapshot.objects.create(
            location=weather.location,
            temperature=weather.temperature,
            feels_like=weather.feelsLike,
            condition=weather.condition,
            icon=weather.icon,
            humidity=weather.humidity,
            wind_dir=weather.windDir,
            wind_scale=weather.windScale,
            obs_time=weather.obsTime,
            raw=_weather_to_raw(weather),
        )

        outfit = Outfit.objects.create(
            user=request.user,
            top=suggested_top,
            bottom=suggested_bottom,
            recommendation_text=recommendation_text,
            weather=weather_snapshot,
        )

        history = OutfitHistory.objects.create(
            user=request.user,
            outfit=outfit,
        )

        serializer = OutfitSerializer(outfit, context={"request": request})
        history_serializer = OutfitHistorySerializer(history, context={"request": request})

        return Response(
            {
                "weather": weather_snapshot.raw,
                "seasons": seasons,
                "outfit": serializer.data,
                "history": history_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
