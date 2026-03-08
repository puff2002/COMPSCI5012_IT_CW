from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OutfitHistoryViewSet, RecommendView

router = DefaultRouter()
router.register(r"history", OutfitHistoryViewSet, basename="outfit-history")

urlpatterns = [
    path("recommend/", RecommendView.as_view(), name="outfit-recommend"),
    path("", include(router.urls)),
]
