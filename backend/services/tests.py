from django.test import SimpleTestCase

from services.openrouter import _extract_json


class OpenRouterParsingTests(SimpleTestCase):
    def test_extract_json_rejects_json_arrays(self):
        with self.assertRaisesMessage(ValueError, "Expected JSON object from model response, got list"):
            _extract_json('[{"category": "top"}]')
