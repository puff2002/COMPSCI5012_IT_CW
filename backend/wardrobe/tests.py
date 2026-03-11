import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from domain.clothes import ClothesSemantics
from services.dashscope_service import ClothesRecognitionError
from .models import ClothingItem

User = get_user_model()


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class WardrobeUploadTests(APITestCase):
    def setUp(self):
        self._media_root = tempfile.mkdtemp(prefix="wardrobe-test-media-")
        self.user = User.objects.create_user(
            username="closet-user",
            email="closet@example.com",
            password="Passw0rd!",
        )
        login_resp = self.client.post(
            "/api/auth/user/login/",
            {"username": "closet-user", "password": "Passw0rd!"},
            format="json",
        )
        self.access = login_resp.data["access"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.access}"}
        self.override = override_settings(MEDIA_ROOT=self._media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self._media_root, ignore_errors=True)
        super().tearDown()

    @patch("wardrobe.views.analyze_clothes", new_callable=AsyncMock)
    def test_upload_returns_analysis_from_dashscope_semantics(self, mock_analyze: AsyncMock):
        mock_analyze.return_value = ClothesSemantics(
            detected=True,
            category="top",
            item="T-shirt",
            style_semantics=["casual"],
            season_semantics=["summer"],
            usage_semantics=["daily"],
            color_semantics="light",
            description="A casual summer T-shirt",
        )
        upload = SimpleUploadedFile("shirt.png", PNG_BYTES, content_type="image/png")

        response = self.client.post(
            "/api/wardrobe/items/upload/",
            {"file": upload},
            format="multipart",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category"], "top")
        self.assertEqual(response.data["item"], "T-shirt")
        self.assertEqual(response.data["style_semantics"], ["casual"])
        analyze_args = mock_analyze.await_args
        self.assertIsNotNone(analyze_args)
        self.assertEqual(analyze_args.kwargs["mime_type"], "image/jpeg")
        self.assertGreater(len(analyze_args.args[0]), 0)

    @patch("wardrobe.views.analyze_clothes", new_callable=AsyncMock)
    def test_upload_returns_400_when_dashscope_analysis_fails(self, mock_analyze: AsyncMock):
        mock_analyze.side_effect = ValueError("bad model output")
        upload = SimpleUploadedFile("shirt.png", PNG_BYTES, content_type="image/png")

        response = self.client.post(
            "/api/wardrobe/items/upload/",
            {"file": upload},
            format="multipart",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "image analyze failed: bad model output")

    @patch("wardrobe.views.analyze_clothes", new_callable=AsyncMock)
    def test_upload_returns_422_when_no_clothing_is_detected(self, mock_analyze: AsyncMock):
        mock_analyze.side_effect = ClothesRecognitionError("No clothing item detected in the image")
        upload = SimpleUploadedFile("shirt.png", PNG_BYTES, content_type="image/png")

        response = self.client.post(
            "/api/wardrobe/items/upload/",
            {"file": upload},
            format="multipart",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data["detail"], "No clothing item detected in the image")
        self.assertEqual(response.data["code"], "recognition_failed")

    def test_upload_returns_400_for_invalid_image_bytes(self):
        upload = SimpleUploadedFile("bad.jpg", b"not-an-image", content_type="image/jpeg")

        response = self.client.post(
            "/api/wardrobe/items/upload/",
            {"file": upload},
            format="multipart",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "unsupported or corrupted image")

    def test_create_item_stores_uploaded_image_with_uuid_filename(self):
        upload = SimpleUploadedFile("summer-shirt.png", PNG_BYTES, content_type="image/png")

        response = self.client.post(
            "/api/wardrobe/items/",
            {
                "category": "top",
                "item": "Summer Shirt",
                "style_semantics": '["casual"]',
                "season_semantics": '["summer"]',
                "usage_semantics": '["daily"]',
                "color_semantics": "light",
                "description": "Lightweight shirt",
                "image": upload,
            },
            format="multipart",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = ClothingItem.objects.get(pk=response.data["id"])
        self.assertTrue(item.image.name.startswith("items/"))
        self.assertNotIn("summer-shirt", item.image.name)

        stored_name = Path(item.image.name).name
        self.assertRegex(stored_name, r"^[0-9a-f-]{36}\.png$")
        self.assertTrue(Path(self._media_root, item.image.name).exists())
