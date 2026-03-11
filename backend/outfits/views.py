from asgiref.sync import async_to_sync
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from services.recommendation import (
    build_recommendation_text,
    get_llm_recommendation,
    score_clothing_match,
)
from services.weather import get_season_from_weather, get_weather_by_coordinates
from wardrobe.models import ClothingItem

from .models import Outfit, OutfitHistory
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


def _select_best_item(
    items: list[ClothingItem],
    category: str,
    criteria: dict[str, object],
    fallback_seasons: list[str],
) -> ClothingItem | None:
    category_items = [item for item in items if item.category == category]
    if not category_items:
        return None

    scored = []
    for item in category_items:
        prompt_item = _to_prompt_item(item)
        score = score_clothing_match(prompt_item, criteria, fallback_seasons)
        scored.append((score, item.created_at, item))

    scored.sort(key=lambda value: (-value[0], value[1], value[2].id))
    return scored[0][2]


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
        prompt_items = [_to_prompt_item(item) for item in items]
        tops = [item for item in prompt_items if item["category"] == "top"]
        bottoms = [item for item in prompt_items if item["category"] == "bottom"]
        shoes = [item for item in prompt_items if item["category"] == "shoes"]

        try:
            recommendation = async_to_sync(get_llm_recommendation)(
                weather,
                seasons,
                tops,
                bottoms,
                shoes,
            )
        except Exception:
            return Response({"detail": "recommendation unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        criteria = recommendation["recommendations"]
        suggested_top = _select_best_item(items, "top", criteria["top"], seasons)
        suggested_bottom = _select_best_item(items, "bottom", criteria["bottom"], seasons)
        suggested_shoes = _select_best_item(items, "shoes", criteria["shoes"], seasons)
        recommendation_text = build_recommendation_text(
            recommendation,
            top=_to_prompt_item(suggested_top) if suggested_top else None,
            bottom=_to_prompt_item(suggested_bottom) if suggested_bottom else None,
            shoes=_to_prompt_item(suggested_shoes) if suggested_shoes else None,
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
                "recommendation": recommendation,
                "outfit": serializer.data,
                "history": history_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
