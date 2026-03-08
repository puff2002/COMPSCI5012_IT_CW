from rest_framework import serializers

from wardrobe.serializers import ClothingItemSerializer
from .models import Outfit, OutfitHistory, WeatherSnapshot


class WeatherSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherSnapshot
        fields = (
            "id",
            "location",
            "temperature",
            "feels_like",
            "condition",
            "icon",
            "humidity",
            "wind_dir",
            "wind_scale",
            "obs_time",
            "raw",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class OutfitSerializer(serializers.ModelSerializer):
    top_detail = ClothingItemSerializer(source="top", read_only=True)
    bottom_detail = ClothingItemSerializer(source="bottom", read_only=True)
    shoes_detail = ClothingItemSerializer(source="shoes", read_only=True)
    weather_detail = WeatherSnapshotSerializer(source="weather", read_only=True)

    class Meta:
        model = Outfit
        fields = (
            "id",
            "top",
            "bottom",
            "shoes",
            "top_detail",
            "bottom_detail",
            "shoes_detail",
            "recommendation_text",
            "weather",
            "weather_detail",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class OutfitHistorySerializer(serializers.ModelSerializer):
    outfit_detail = OutfitSerializer(source="outfit", read_only=True)

    class Meta:
        model = OutfitHistory
        fields = (
            "id",
            "outfit",
            "outfit_detail",
            "rating",
            "feedback",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
