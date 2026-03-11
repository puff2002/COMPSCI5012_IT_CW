from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OutfitHistoryViewSet, OutfitSimulationView, RecommendView

router = DefaultRouter()
router.register(r"history", OutfitHistoryViewSet, basename="outfit-history")

urlpatterns = [
    path("recommend/", RecommendView.as_view(), name="outfit-recommend"),
    path("<int:outfit_id>/simulate-image/", OutfitSimulationView.as_view(), name="outfit-simulate-image"),
    path("", include(router.urls)),
]
