from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from outfits.models import Outfit, OutfitHistory
from services.weather import WeatherInfo
from wardrobe.models import ClothingItem

User = get_user_model()


class OutfitRecommendationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="outfit-user",
            email="outfit@example.com",
            password="Passw0rd!",
        )
        login_resp = self.client.post(
            "/api/auth/user/login/",
            {"username": "outfit-user", "password": "Passw0rd!"},
            format="json",
        )
        self.access = login_resp.data["access"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access}"}
        self.top = ClothingItem.objects.create(
            owner=self.user,
            category="top",
            item="Oxford Shirt",
            style_semantics=["smart"],
            season_semantics=["spring"],
            usage_semantics=["work"],
            color_semantics="light",
            description="A clean work shirt",
        )
        self.bottom = ClothingItem.objects.create(
            owner=self.user,
            category="bottom",
            item="Chinos",
            style_semantics=["smart-casual"],
            season_semantics=["spring"],
            usage_semantics=["work"],
            color_semantics="neutral",
            description="Straight-fit chinos",
        )
        self.shoes = ClothingItem.objects.create(
            owner=self.user,
            category="shoes",
            item="Leather Loafers",
            style_semantics=["smart-casual"],
            season_semantics=["spring"],
            usage_semantics=["work"],
            color_semantics="brown",
            description="Polished leather loafers",
        )
        self.cold_top = ClothingItem.objects.create(
            owner=self.user,
            category="top",
            item="Heavy Knit",
            style_semantics=["casual"],
            season_semantics=["winter"],
            usage_semantics=["daily"],
            color_semantics="dark",
            description="A heavy winter knit",
        )

    def _weather(self) -> WeatherInfo:
        return WeatherInfo(
            temperature=18.0,
            feelsLike=17.0,
            condition="Partly cloudy",
            icon="102",
            humidity=60.0,
            windDir="SE",
            windScale="3",
            location="Melbourne, Victoria, Australia",
            obsTime="2026-03-11T10:00",
        )

    @patch("outfits.views.get_weather_by_coordinates", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_returns_outfit_and_history(self, mock_recommendation: AsyncMock, mock_get_weather: AsyncMock):
        mock_get_weather.return_value = self._weather()
        mock_recommendation.return_value = {
            "summary": "A light smart-casual outfit for mild weather.",
            "weather_focus": ["mild", "dry"],
            "recommendations": {
                "top": {
                    "type": "oxford shirt",
                    "season": ["spring"],
                    "color": ["light"],
                    "texture": ["cotton"],
                    "style": ["smart"],
                    "reason": "Breathable and polished.",
                },
                "bottom": {
                    "type": "chinos",
                    "season": ["spring"],
                    "color": ["neutral"],
                    "texture": ["cotton"],
                    "style": ["smart-casual"],
                    "reason": "Comfortable for mild weather.",
                },
                "shoes": {
                    "type": "loafers",
                    "season": ["spring"],
                    "color": ["brown"],
                    "texture": ["leather"],
                    "style": ["smart-casual"],
                    "reason": "Works well in dry conditions.",
                },
            },
        }

        response = self.client.post(
            "/api/outfits/recommend/",
            {"latitude": -37.8136, "longitude": 144.9631},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["outfit"]["recommendation_text"], "A light smart-casual outfit for mild weather.")
        self.assertEqual(response.data["outfit"]["top"], self.top.id)
        self.assertEqual(response.data["outfit"]["bottom"], self.bottom.id)
        self.assertEqual(response.data["outfit"]["shoes"], self.shoes.id)
        self.assertEqual(response.data["recommendation"]["recommendations"]["top"]["type"], "oxford shirt")
        self.assertEqual(Outfit.objects.count(), 1)
        self.assertEqual(OutfitHistory.objects.count(), 1)
        args = mock_recommendation.await_args.args
        self.assertEqual(args[1], ["spring", "autumn"])
        self.assertEqual(args[2][0]["item"], "Oxford Shirt")
        self.assertEqual(args[2][0]["category"], "top")
        self.assertEqual(args[3][0]["item"], "Chinos")
        self.assertEqual(args[4][0]["item"], "Leather Loafers")

    @patch("outfits.views.get_weather_by_coordinates", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_uses_fallback_category_pool_when_no_seasonal_match(
        self,
        mock_recommendation: AsyncMock,
        mock_get_weather: AsyncMock,
    ):
        mock_get_weather.return_value = WeatherInfo(
            temperature=3.0,
            feelsLike=1.0,
            condition="Overcast",
            icon="104",
            humidity=80.0,
            windDir="NE",
            windScale="4",
            location="Melbourne, Victoria, Australia",
            obsTime="2026-03-11T06:00",
        )
        mock_recommendation.return_value = {
            "summary": "Prioritize warmer upper layers for the cold morning.",
            "weather_focus": ["cold", "overcast"],
            "recommendations": {
                "top": {
                    "type": "knit",
                    "season": ["winter"],
                    "color": ["dark"],
                    "texture": ["heavy"],
                    "style": ["casual"],
                    "reason": "Adds warmth.",
                },
                "bottom": {
                    "type": "chinos",
                    "season": ["autumn"],
                    "color": ["neutral"],
                    "texture": ["structured"],
                    "style": ["smart-casual"],
                    "reason": "Only bottom available.",
                },
                "shoes": {
                    "type": "loafers",
                    "season": ["autumn"],
                    "color": ["brown"],
                    "texture": ["leather"],
                    "style": ["smart-casual"],
                    "reason": "Only footwear available.",
                },
            },
        }

        response = self.client.post(
            "/api/outfits/recommend/",
            {"latitude": -37.8136, "longitude": 144.9631},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["outfit"]["top"], self.cold_top.id)
        self.assertEqual(response.data["outfit"]["bottom"], self.bottom.id)
        self.assertEqual(response.data["outfit"]["shoes"], self.shoes.id)
        args = mock_recommendation.await_args.args
        self.assertEqual({item["item"] for item in args[2]}, {"Oxford Shirt", "Heavy Knit"})
        self.assertEqual({item["item"] for item in args[3]}, {"Chinos"})
        self.assertEqual({item["item"] for item in args[4]}, {"Leather Loafers"})

    @patch("outfits.views.get_weather_by_coordinates", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_returns_503_when_weather_unavailable(
        self,
        _mock_recommendation: AsyncMock,
        mock_get_weather: AsyncMock,
    ):
        mock_get_weather.return_value = None

        response = self.client.post(
            "/api/outfits/recommend/",
            {"latitude": -37.8136, "longitude": 144.9631},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(Outfit.objects.count(), 0)
        self.assertEqual(OutfitHistory.objects.count(), 0)
    @patch("outfits.views.get_weather_by_coordinates", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_returns_503_when_recommendation_unavailable(
        self,
        mock_recommendation: AsyncMock,
        mock_get_weather: AsyncMock,
    ):
        mock_get_weather.return_value = self._weather()
        mock_recommendation.side_effect = ValueError("DashScope down")

        response = self.client.post(
            "/api/outfits/recommend/",
            {"latitude": -37.8136, "longitude": 144.9631},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["detail"], "recommendation unavailable")
        self.assertEqual(Outfit.objects.count(), 0)
        self.assertEqual(OutfitHistory.objects.count(), 0)

    def test_simulate_image_returns_400_without_weather_snapshot(self):
        outfit = Outfit.objects.create(
            user=self.user,
            top=self.top,
            bottom=self.bottom,
            shoes=self.shoes,
            recommendation_text="A light smart-casual outfit for mild weather.",
            weather=None,
        )
        outfit.weather_id = None
        outfit.save(update_fields=["weather"])
