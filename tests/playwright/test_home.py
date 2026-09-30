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

    actual_text = page.locator("h1").first.text_content()
    assert actual_text == "We build AI products and integrations that move your business faster."


@pytest.mark.regression
def test_favicon_download_filename(page):
    home = HomePage(page)
    home.load()

    favicon = page.locator('link[rel="icon"]')
    favicon_url = favicon.get_attribute("href")
    assert favicon_url is not None

    with page.expect_download() as download_info:
        page.evaluate(
            """url => {
                const link = document.createElement("a");
                link.href = url;
                link.download = "";
                document.body.append(link);
                link.click();
                link.remove();
            }""",
            favicon_url,
        )

    download = download_info.value
    assert download.suggested_filename == "favicon.svg"