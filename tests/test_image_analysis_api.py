import base64
from io import BytesIO
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image
from rest_framework.test import APIClient


class ImageAnalysisApiTests(SimpleTestCase):
    def make_png(self, size=None):
        output = BytesIO()
        Image.new("RGB", (1, 1), color="red").save(output, format="PNG")
        image_data = output.getvalue()
        if size:
            image_data += b"\0" * (size - len(image_data))
        return image_data

    @patch("webapp.views.requests.post")
    def test_sends_image_and_question_to_gemma_and_returns_answer(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"response": "A red pixel."}
        mock_post.return_value = mock_response
        image_data = self.make_png(size=11 * 1024)

        response = APIClient().post(
            "/api/ai-lab/image-analysis/",
            {
                "image": SimpleUploadedFile("sample.png", image_data, content_type="image/png"),
                "question": "What is in this image?",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"answer": "A red pixel."})
        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.kwargs["json"],
            {
                "model": "gemma3:4b",
                "prompt": "What is in this image?",
                "images": [base64.b64encode(image_data).decode("ascii")],
                "stream": False,
            },
        )

    @patch("webapp.views.requests.post")
    def test_rejects_images_larger_than_11_kib(self, mock_post):
        image_data = self.make_png(size=11 * 1024 + 1)

        response = APIClient().post(
            "/api/ai-lab/image-analysis/",
            {
                "image": SimpleUploadedFile("sample.png", image_data, content_type="image/png"),
                "question": "What is in this image?",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("11 KB or smaller", str(response.data))
        mock_post.assert_not_called()