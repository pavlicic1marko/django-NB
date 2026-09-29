import os

import pytest


@pytest.mark.test
def test_get_news_from_api(playwright):
	base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
	request = playwright.request.new_context()

	try:
		response = request.get(f"{base_url}/api/news/")
		assert response.status == 200, (
			f"News API returned HTTP {response.status} at {base_url}"
		)

		news_items = response.json()
		assert isinstance(news_items, list)

		expected_fields = {
			"id",
			"language",
			"title",
			"slug",
			"text",
			"date",
			"image",
			"alt_text",
			"created_at",
		}
		for news_item in news_items:
			assert expected_fields.issubset(news_item)
	finally:
		request.dispose()
