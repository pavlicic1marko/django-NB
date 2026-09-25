def test_home_page(page):
    page.goto("http://127.0.0.1:8000/")

    assert page.title() != ""
    assert page.locator("h1", has_text="We build AI products and integrations that move your business faster.").is_visible()

def test_about_page(page):
    page.goto("http://127.0.0.1:8000/about-us/")

    assert page.title() != ""
    assert page.locator("h1", has_text="Who We Are").is_visible()