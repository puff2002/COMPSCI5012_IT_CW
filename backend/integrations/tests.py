from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from services.weather import CityInfo, WeatherInfo, _decode_location_token, _encode_location_token

User = get_user_model()


class WeatherServiceTests(SimpleTestCase):
    def test_location_token_round_trip(self):
        token = _encode_location_token(
            {
                "name": "Melbourne",
                "admin1": "Victoria",
                "admin2": "Melbourne",
                "country": "Australia",
                "latitude": -37.814,
                "longitude": 144.96332,
            }
        )

        decoded = _decode_location_token(token)

        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["name"], "Melbourne")
        self.assertEqual(decoded["adm1"], "Victoria")
        self.assertEqual(decoded["country"], "Australia")
        self.assertEqual(decoded["lat"], -37.814)
        self.assertEqual(decoded["lon"], 144.96332)


class IntegrationApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="weather-user",
            email="weather@example.com",
            password="Passw0rd!",
        )
        login_resp = self.client.post(
            "/api/auth/user/login/",
            {"username": "weather-user", "password": "Passw0rd!"},
            format="json",
        )
        self.access = login_resp.data["access"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access}"}

    def test_config_response_excludes_qweather_fields(self):
        save_resp = self.client.post(
            "/api/integrations/config/",
            {
                "api_base": "https://example.com",
                "api_key": "secret-llm-key",
                "model": "gemini-2.0-flash",
                "removebg_api_key": "removebg-secret",
                "bg_removal_method": "removebg",
            },
            format="json",
            **self.auth_headers,
        )
        self.assertEqual(save_resp.status_code, status.HTTP_200_OK)
        self.assertNotIn("qweather_api_key", save_resp.data)
        self.assertNotIn("qweather_api_host", save_resp.data)

        get_resp = self.client.get("/api/integrations/config/", **self.auth_headers)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertNotIn("qweather_api_key_masked", get_resp.data)
        self.assertNotIn("has_qweather_key", get_resp.data)
        self.assertNotIn("qweather_api_host", get_resp.data)
        self.assertEqual(get_resp.data["api_base"], "https://example.com")
        self.assertTrue(get_resp.data["has_api_key"])
        self.assertTrue(get_resp.data["has_removebg_key"])

    @patch("integrations.views.search_city")
    def test_weather_search_returns_backend_shape(self, mock_search_city):
        mock_search_city.return_value = [
            CityInfo(
                name="Melbourne",
                id="encoded-token",
                adm1="Victoria",
                adm2="Melbourne",
                country="Australia",
                lat="-37.814",
                lon="144.96332",
            )
        ]

        resp = self.client.get("/api/integrations/weather/search/?query=melbourne", **self.auth_headers)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]["id"], "encoded-token")
        self.assertEqual(resp.data[0]["name"], "Melbourne")

    @patch("integrations.views.get_weather")
    def test_weather_now_returns_backend_shape(self, mock_get_weather):
        mock_get_weather.return_value = WeatherInfo(
            temperature=21.5,
            feelsLike=20.8,
            condition="Partly cloudy",
            icon="102",
            humidity=61.0,
            windDir="SE",
            windScale="3",
            location="Melbourne, Victoria, Australia",
            obsTime="2026-03-11T10:00",
        )

        resp = self.client.get("/api/integrations/weather/now/?location=encoded-token", **self.auth_headers)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["condition"], "Partly cloudy")
        self.assertEqual(resp.data["windDir"], "SE")
