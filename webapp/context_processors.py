from django.conf import settings
from django.urls import translate_url


def localized_urls(request):
    current_url = request.get_full_path()
    language_urls = {
        language_code: request.build_absolute_uri(translate_url(current_url, language_code))
        for language_code, _ in settings.LANGUAGES
    }
    return {
        "canonical_url": request.build_absolute_uri(current_url),
        "language_urls": language_urls,
        "language_switch_urls": {
            language_code: f"/language/{language_code}/?next={current_url}"
            for language_code, _ in settings.LANGUAGES
        },
    }