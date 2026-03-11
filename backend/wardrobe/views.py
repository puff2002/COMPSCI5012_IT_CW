from asgiref.sync import async_to_sync
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from services.dashscope_service import ClothesRecognitionError, analyze_clothes
from services.images import LLM_INPUT_MAX_DIMENSION, normalize_image_bytes

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

        try:
            raw_bytes, processed_mime_type = normalize_image_bytes(
                upload.read(),
                output_format="JPEG",
                max_dimension=LLM_INPUT_MAX_DIMENSION,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        processed_bytes = raw_bytes

        try:
            semantics = async_to_sync(analyze_clothes)(processed_bytes, mime_type=processed_mime_type)
        except ClothesRecognitionError as exc:
            return Response(
                {"detail": str(exc), "code": "recognition_failed"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as exc:
            return Response({"detail": f"image analyze failed: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "category": semantics.category,
                "item": semantics.item,
                "style_semantics": semantics.style_semantics,
                "season_semantics": semantics.season_semantics,
                "usage_semantics": semantics.usage_semantics,
                "color_semantics": semantics.color_semantics,
                "description": semantics.description,
            },
            status=status.HTTP_200_OK,
        )
