import pytest

from pages.about_page import AboutPage


@pytest.mark.smoke
@pytest.mark.regression
def test_about_page(page):
    about = AboutPage(page)
    about.load()

    assert about.get_title() != ""
    assert about.is_heading_visible()