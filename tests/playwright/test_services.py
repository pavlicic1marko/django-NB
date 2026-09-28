import os
import pytest

@pytest.mark.server
def test_ollama_service_is_up(playwright):
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    request = playwright.request.new_context(timeout=5_000)

    try:
        response = request.get(f"{base_url}/api/tags")
        assert response.status == 200, (
            f"Ollama returned HTTP {response.status} at {base_url}"
        )

        data = response.json()
        assert isinstance(data, dict)
        assert isinstance(data.get("models"), list)
    finally:
        request.dispose()