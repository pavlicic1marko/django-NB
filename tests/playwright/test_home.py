import pytest

from pages.home_page import HomePage


@pytest.mark.smoke
@pytest.mark.regression
def test_home_page(page):
    home = HomePage(page)
    home.load()

    assert home.get_title() != ""
    assert home.is_heading_visible()


@pytest.mark.regression
def test_home_page_heading_is_not_wrong_text(page):
    home = HomePage(page)
    home.load()

    actual_text = home.get_heading_text()
    assert actual_text == "We build AI products and integrations that move your business faster."


@pytest.mark.regression
def test_favicon_download_filename(page):
    home = HomePage(page)
    home.load()

    favicon_url = home.get_favicon_url()
    assert favicon_url is not None

    download = home.download_favicon()
    assert download.suggested_filename == "favicon.svg"


@pytest.mark.regression
def test_home_page_language_switch_to_de(page):
    home = HomePage(page)
    home.load()

    home.switch_language_to_de()

    assert home.get_language_code() == "DE"
    assert "de_flag" in home.get_language_flag_src()
    assert home.get_heading_text() == home.HEADING_TEXT_DE