from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClothingItemViewSet, ClothingUploadView

router = DefaultRouter()
router.register(r"items", ClothingItemViewSet, basename="clothing-item")

urlpatterns = [
    path("items/upload/", ClothingUploadView.as_view(), name="clothing-upload"),
    path("", include(router.urls)),
]
