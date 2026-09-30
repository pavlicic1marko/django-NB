from .base_page import BasePage

class AboutPage(BasePage):
    URL = "http://127.0.0.1:8000/about-us/"
    HEADING_TEXT = "Who We Are"

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("h1", has_text=self.HEADING_TEXT)

    def load(self):
        self.goto(self.URL)

    def is_heading_visible(self):
        return self.heading.is_visible()