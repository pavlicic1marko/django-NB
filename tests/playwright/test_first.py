import pytest
from pages.home_page import HomePage
from pages.about_page import AboutPage

@pytest.mark.smoke
@pytest.mark.regression
def test_home_page(page):
    home = HomePage(page)
    home.load()

    assert home.get_title() != ""
    assert home.is_heading_visible()

@pytest.mark.smoke
@pytest.mark.regression
def test_about_page(page):
    about = AboutPage(page)
    about.load()

    assert about.get_title() != ""
    assert about.is_heading_visible()

@pytest.mark.regression
def test_home_page_heading_is_not_wrong_text(page):
    home = HomePage(page)
    home.load()

    actual_text = page.locator("h1").first.text_content()
    assert actual_text != "This is definitely the wrong heading"