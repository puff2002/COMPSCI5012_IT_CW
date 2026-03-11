from django.test import SimpleTestCase

from services.dashscope_service import _extract_json


class DashScopeParsingTests(SimpleTestCase):
    def test_extract_json_rejects_json_arrays(self):
        with self.assertRaisesMessage(ValueError, "Expected JSON object from model response, got list"):
            _extract_json('[{"category": "top"}]')
