import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage


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


@pytest.mark.regression
def test_home_page_profile_menu_login_navigates_to_login_page(page):
    home = HomePage(page)
    home.load()

    home.open_profile_menu()
    home.click_login()

    login = LoginPage(page)
    assert page.url.endswith("/login/")
    assert login.is_login_button_visible()


@pytest.mark.regression
def test_login_page_register_button_navigates_to_register_page(page):
    login = LoginPage(page)
    login.load()

    assert page.get_by_text("Don't have an account?").is_visible()
    login.click_register()

    register = RegisterPage(page)
    assert page.url.endswith("/register/")
    assert register.is_create_account_button_visible()


@pytest.mark.regression
def test_home_page_profile_menu_register_navigates_to_register_page(page):
    home = HomePage(page)
    home.load()

    home.open_profile_menu()
    home.click_register()

    register = RegisterPage(page)
    assert page.url.endswith("/register/")
    assert register.is_create_account_button_visible()