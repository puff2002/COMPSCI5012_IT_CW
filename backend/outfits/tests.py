from asgiref.sync import async_to_sync
from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from outfits.models import Outfit, OutfitHistory
from services.recommendation import get_llm_recommendation
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

    @patch("outfits.views.get_weather_for_query", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_returns_outfit_and_history(self, mock_recommendation: AsyncMock, mock_get_weather: AsyncMock):
        mock_get_weather.return_value = self._weather()
        mock_recommendation.return_value = "Wear the Oxford Shirt with the Chinos."

        response = self.client.post(
            "/api/outfits/recommend/",
            {"location": "melbourne"},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["outfit"]["recommendation_text"], "Wear the Oxford Shirt with the Chinos.")
        self.assertEqual(response.data["outfit"]["top"], self.top.id)
        self.assertEqual(response.data["outfit"]["bottom"], self.bottom.id)
        self.assertEqual(Outfit.objects.count(), 1)
        self.assertEqual(OutfitHistory.objects.count(), 1)
        args = mock_recommendation.await_args.args
        self.assertEqual(args[1], ["spring", "autumn"])
        self.assertEqual(args[2][0]["item"], "Oxford Shirt")
        self.assertEqual(args[2][0]["category"], "top")
        self.assertEqual(args[3][0]["item"], "Chinos")

    @patch("outfits.views.get_weather_for_query", new_callable=AsyncMock)
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
        mock_recommendation.return_value = "Use the best available lightweight pieces."

        response = self.client.post(
            "/api/outfits/recommend/",
            {"location": "melbourne"},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = mock_recommendation.await_args.args
        top_items = args[2]
        bottom_items = args[3]
        self.assertEqual({item["item"] for item in top_items}, {"Heavy Knit"})
        self.assertEqual({item["item"] for item in bottom_items}, {"Chinos"})

    @patch("outfits.views.get_weather_for_query", new_callable=AsyncMock)
    @patch("outfits.views.get_llm_recommendation", new_callable=AsyncMock)
    def test_recommend_returns_503_when_weather_unavailable(
        self,
        _mock_recommendation: AsyncMock,
        mock_get_weather: AsyncMock,
    ):
        mock_get_weather.return_value = None

        response = self.client.post(
            "/api/outfits/recommend/",
            {"location": "melbourne"},
            format="json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(Outfit.objects.count(), 0)
        self.assertEqual(OutfitHistory.objects.count(), 0)


class RecommendationServiceTests(APITestCase):
    @patch("services.recommendation.chat_completion", new_callable=AsyncMock)
    def test_get_llm_recommendation_falls_back_when_openrouter_fails(self, mock_chat_completion: AsyncMock):
        mock_chat_completion.side_effect = ValueError("OpenRouter down")
        weather = WeatherInfo(
            temperature=29.0,
            feelsLike=31.0,
            condition="Clear sky",
            icon="100",
            humidity=40.0,
            windDir="N",
            windScale="2",
            location="Melbourne, Victoria, Australia",
            obsTime="2026-03-11T13:00",
        )

        result = async_to_sync(get_llm_recommendation)(weather, ["summer"], [], [])

        self.assertIn("breathable summer clothing", result)
