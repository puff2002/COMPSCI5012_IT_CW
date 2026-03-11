import random
from base64 import b64encode

from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from services.openrouter import generate_image
from services.recommendation import build_outfit_image_prompt, get_llm_recommendation
from services.weather import WeatherInfo, get_season_from_weather, get_weather_by_coordinates
from wardrobe.models import ClothingItem

from .models import Outfit, OutfitHistory, WeatherSnapshot
from .serializers import OutfitHistorySerializer, OutfitSerializer


def _weather_to_raw(weather):
    if hasattr(weather, "model_dump"):
        return weather.model_dump()
    if hasattr(weather, "dict"):
        return weather.dict()
    return {}


def _to_prompt_item(item: ClothingItem) -> dict[str, object]:
    return {
        "id": item.id,
        "item": item.item,
        "category": item.category,
        "style_semantics": item.style_semantics,
        "season_semantics": item.season_semantics,
        "usage_semantics": item.usage_semantics,
        "color_semantics": item.color_semantics,
        "description": item.description,
    }


def _snapshot_to_weather_info(snapshot: WeatherSnapshot) -> WeatherInfo:
    return WeatherInfo(
        temperature=snapshot.temperature,
        feelsLike=snapshot.feels_like,
        condition=snapshot.condition,
        icon=snapshot.icon,
        humidity=snapshot.humidity or 0.0,
        windDir=snapshot.wind_dir,
        windScale=snapshot.wind_scale,
        location=snapshot.location,
        obsTime=snapshot.obs_time,
    )


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
        try:
            latitude = float(request.data.get("latitude"))
            longitude = float(request.data.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {"detail": "latitude and longitude required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        weather = async_to_sync(get_weather_by_coordinates)(latitude, longitude)
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
        shoes = [item for item in items if item.category == "shoes" and is_suitable(item)]
        if not shoes:
            shoes = [item for item in items if item.category == "shoes"]

        suggested_top = random.choice(tops) if tops else None
        suggested_bottom = random.choice(bottoms) if bottoms else None
        suggested_shoes = random.choice(shoes) if shoes else None

        try:
            recommendation_text = async_to_sync(get_llm_recommendation)(
                weather,
                seasons,
                [_to_prompt_item(item) for item in tops],
                [_to_prompt_item(item) for item in bottoms],
                [_to_prompt_item(item) for item in shoes],
            )
        except Exception:
            return Response({"detail": "recommendation unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
            shoes=suggested_shoes,
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


class OutfitSimulationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, outfit_id: int):
        outfit = get_object_or_404(Outfit.objects.select_related("top", "bottom", "shoes", "weather"), pk=outfit_id, user=request.user)
        weather = outfit.weather
        if not weather:
            return Response({"detail": "weather unavailable for outfit"}, status=status.HTTP_400_BAD_REQUEST)

        raw_weather = weather.raw or {}
        weather_info = _snapshot_to_weather_info(weather)
        seasons = get_season_from_weather(weather_info)
        top_item = _to_prompt_item(outfit.top) if outfit.top else None
        bottom_item = _to_prompt_item(outfit.bottom) if outfit.bottom else None
        shoes_item = _to_prompt_item(outfit.shoes) if outfit.shoes else None
        prompt = build_outfit_image_prompt(
            weather_info,
            seasons,
            top=top_item,
            bottom=bottom_item,
            shoes=shoes_item,
            recommendation_text=outfit.recommendation_text,
        )

        try:
            image_bytes = async_to_sync(generate_image)(prompt)
        except Exception:
            return Response({"detail": "outfit image generation unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {
                "outfit_id": outfit.id,
                "prompt": prompt,
                "image_url": f"data:image/png;base64,{b64encode(image_bytes).decode('ascii')}",
                "weather": raw_weather,
                "seasons": seasons,
            },
            status=status.HTTP_200_OK,
        )
