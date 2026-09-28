import os

from pages.base_page import BasePage


class AISolutionsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        self.url = f"{base_url}/ai-solutions/"
        self.heading = page.get_by_role("heading", level=1).first

    def load(self):
        self.goto(self.url)

    def is_heading_visible(self):
        return self.heading.is_visible()