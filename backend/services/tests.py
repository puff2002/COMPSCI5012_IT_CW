from django.test import SimpleTestCase

from services.dashscope_service import _extract_generated_image_reference, _extract_json


class DashScopeParsingTests(SimpleTestCase):
    def test_extract_json_rejects_json_arrays(self):
        with self.assertRaisesMessage(ValueError, "Expected JSON object from model response, got list"):
            _extract_json('[{"category": "top"}]')

    def test_extract_generated_image_reference_from_dashscope_message(self):
        response = {
            "output": {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"image": "https://example.com/generated.png"},
                            ]
                        }
                    }
                ]
            }
        }

        self.assertEqual(
            _extract_generated_image_reference(response),
            "https://example.com/generated.png",
        )

    def test_extract_generated_image_reference_raises_when_missing(self):
        with self.assertRaisesMessage(ValueError, "Image generation response did not include an image output"):
            _extract_generated_image_reference(
                {
                    "output": {
                        "choices": [
                            {
                                "message": {
                                    "content": [{"text": "no image"}]
                                }
                            }
                        ]
                    }
                }
            )
