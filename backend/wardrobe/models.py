from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def clothing_item_image_upload_path(instance, filename: str) -> str:
    extension = Path(filename).suffix.lower() or ".jpg"
    return f"items/{uuid4()}{extension}"


class ClothingItem(models.Model):
    CATEGORY_CHOICES = [
        ("top", "top"),
        ("bottom", "bottom"),
        ("shoes", "shoes"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clothing_items",
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    item = models.CharField(max_length=120)
    style_semantics = models.JSONField(default=list, blank=True)
    season_semantics = models.JSONField(default=list, blank=True)
    usage_semantics = models.JSONField(default=list, blank=True)
    color_semantics = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=clothing_item_image_upload_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.owner_id}:{self.category}:{self.item}"
