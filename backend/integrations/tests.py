from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from services.weather import _decode_location_token, _encode_location_token
from storage.config_store import get_masked_config

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


class ConfigStoreTests(SimpleTestCase):
    def test_masked_config_uses_removebg_defaults_when_no_saved_file(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "llm_config.json"
            with patch("storage.config_store.CONFIG_FILE", temp_path):
                config = get_masked_config()

        self.assertEqual(config["bg_removal_method"], "removebg")
        self.assertFalse(config["has_removebg_key"])


class IntegrationApiTests(APITestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.config_patcher = patch("storage.config_store.CONFIG_FILE", Path(self.temp_dir.name) / "llm_config.json")
        self.config_patcher.start()
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

    def tearDown(self):
        self.config_patcher.stop()
        self.temp_dir.cleanup()

    def test_config_response_only_exposes_removebg_fields(self):
        save_resp = self.client.post(
            "/api/integrations/config/",
            {
                "removebg_api_key": "removebg-secret",
                "bg_removal_method": "removebg",
            },
            format="json",
            **self.auth_headers,
        )
        self.assertEqual(save_resp.status_code, status.HTTP_200_OK)
        self.assertNotIn("api_base", save_resp.data)
        self.assertNotIn("api_key", save_resp.data)
        self.assertNotIn("model", save_resp.data)

        get_resp = self.client.get("/api/integrations/config/", **self.auth_headers)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertNotIn("api_base", get_resp.data)
        self.assertNotIn("api_key_masked", get_resp.data)
        self.assertNotIn("has_api_key", get_resp.data)
        self.assertNotIn("model", get_resp.data)
        self.assertTrue(get_resp.data["has_removebg_key"])
