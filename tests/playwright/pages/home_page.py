from .base_page import BasePage

class HomePage(BasePage):
    URL = "http://127.0.0.1:8000/"
    HEADING_TEXT = "We build AI products and integrations that move your business faster."

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("h1", has_text=self.HEADING_TEXT)
        self.favicon = page.locator('link[rel="icon"]')

    def load(self):
        self.goto(self.URL)

    def is_heading_visible(self):
        return self.heading.is_visible()

    def get_heading_text(self):
        heading_text = self.heading.text_content()
        return " ".join(heading_text.split()) if heading_text else ""

    def get_favicon_url(self):
        return self.favicon.get_attribute("href")

    def download_favicon(self):
        favicon_url = self.get_favicon_url()
        if favicon_url is None:
            raise AssertionError("Favicon link has no href")

        with self.page.expect_download() as download_info:
            self.page.evaluate(
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

        return download_info.value