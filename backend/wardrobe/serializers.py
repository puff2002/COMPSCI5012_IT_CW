from rest_framework import serializers

from .models import ClothingItem


class ClothingItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ClothingItem
        fields = (
            "id",
            "category",
            "item",
            "style_semantics",
            "season_semantics",
            "usage_semantics",
            "color_semantics",
            "description",
            "image",
            "image_url",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ""
