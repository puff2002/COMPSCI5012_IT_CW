import uuid

from asgiref.sync import async_to_sync
from django.core.files.base import ContentFile
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from services.gemini import analyze_clothes
from services.removebg import remove_background_api
from services.segment import remove_background
from storage.config_store import load_config

from .models import ClothingItem
from .serializers import ClothingItemSerializer


class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ClothingItem.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-category")
    def by_category(self, request):
        items = self.get_queryset()
        grouped = {
            "top": [item for item in items if item.category == "top"],
            "bottom": [item for item in items if item.category == "bottom"],
            "shoes": [item for item in items if item.category == "shoes"],
        }
        return Response(
            {
                "tops": self.get_serializer(grouped["top"], many=True).data,
                "bottoms": self.get_serializer(grouped["bottom"], many=True).data,
                "shoes": self.get_serializer(grouped["shoes"], many=True).data,
            }
        )


class ClothingUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file") or request.FILES.get("image")
        if not upload:
            return Response({"detail": "file required"}, status=status.HTTP_400_BAD_REQUEST)
        if not upload.content_type or not upload.content_type.startswith("image/"):
            return Response({"detail": "only image files supported"}, status=status.HTTP_400_BAD_REQUEST)

        raw_bytes = upload.read()

        config = load_config()
        if config.bg_removal_method == "removebg" and config.removebg_api_key:
            try:
                processed_bytes = async_to_sync(remove_background_api)(
                    raw_bytes,
                    config.removebg_api_key,
                )
            except Exception:
                processed_bytes = remove_background(raw_bytes)
        else:
            processed_bytes = remove_background(raw_bytes)

        try:
            semantics = async_to_sync(analyze_clothes)(processed_bytes)
        except Exception as exc:
            return Response({"detail": f"image analyze failed: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        item = ClothingItem.objects.create(
            owner=request.user,
            category=semantics.category,
            item=semantics.item,
            style_semantics=semantics.style_semantics,
            season_semantics=semantics.season_semantics,
            usage_semantics=semantics.usage_semantics,
            color_semantics=semantics.color_semantics,
            description=semantics.description,
        )

        filename = f"{uuid.uuid4()}.png"
        item.image.save(filename, ContentFile(processed_bytes), save=True)

        serializer = ClothingItemSerializer(item, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
