from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from storage.config_store import get_masked_config, update_config


class ConfigView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(get_masked_config())

    def post(self, request):
        config = update_config(
            removebg_api_key=request.data.get("removebg_api_key"),
            bg_removal_method=request.data.get("bg_removal_method"),
        )
        if hasattr(config, "model_dump"):
            data = config.model_dump()
        else:
            data = config.dict()
        return Response({"message": "updated", **data})
