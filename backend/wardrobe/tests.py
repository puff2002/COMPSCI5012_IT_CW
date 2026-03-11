from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from domain.clothes import ClothesSemantics
from wardrobe.models import ClothingItem

User = get_user_model()


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xd9\xa3\x1d"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class WardrobeUploadTests(APITestCase):
    def setUp(self):
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

    @patch("wardrobe.views.remove_background", return_value=PNG_BYTES)
    @patch("wardrobe.views.analyze_clothes", new_callable=AsyncMock)
    def test_upload_creates_item_from_openrouter_semantics(self, mock_analyze: AsyncMock, _mock_remove_background):
        mock_analyze.return_value = ClothesSemantics(
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ClothingItem.objects.count(), 1)
        item = ClothingItem.objects.get()
        self.assertEqual(item.owner, self.user)
        self.assertEqual(item.category, "top")
        self.assertEqual(item.item, "T-shirt")
        self.assertEqual(item.style_semantics, ["casual"])
        self.assertTrue(item.image.name.endswith(".png"))
        mock_analyze.assert_awaited_once()

    @patch("wardrobe.views.remove_background", return_value=PNG_BYTES)
    @patch("wardrobe.views.analyze_clothes", new_callable=AsyncMock)
    def test_upload_returns_400_when_openrouter_analysis_fails(self, mock_analyze: AsyncMock, _mock_remove_background):
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
        self.assertEqual(ClothingItem.objects.count(), 0)
