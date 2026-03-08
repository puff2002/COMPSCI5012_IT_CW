from django.conf import settings
from django.db import models

from wardrobe.models import ClothingItem


class WeatherSnapshot(models.Model):
    location = models.CharField(max_length=120)
    temperature = models.FloatField()
    feels_like = models.FloatField()
    condition = models.CharField(max_length=120)
    icon = models.CharField(max_length=20, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    wind_dir = models.CharField(max_length=50, blank=True)
    wind_scale = models.CharField(max_length=20, blank=True)
    obs_time = models.CharField(max_length=64, blank=True)
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.location} {self.temperature}C"


class Outfit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="outfits",
    )
    top = models.ForeignKey(
        ClothingItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outfit_tops",
    )
    bottom = models.ForeignKey(
        ClothingItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outfit_bottoms",
    )
    shoes = models.ForeignKey(
        ClothingItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outfit_shoes",
    )
    recommendation_text = models.TextField(blank=True)
    weather = models.ForeignKey(
        WeatherSnapshot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outfits",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Outfit({self.user_id})"


class OutfitHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="outfit_history",
    )
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.CASCADE,
        related_name="history_entries",
    )
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"History({self.user_id}:{self.outfit_id})"
