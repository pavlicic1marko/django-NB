def test_home_page(page):
    page.goto("http://127.0.0.1:8000/")

    assert page.title() != ""
    assert page.locator("body").is_visible()