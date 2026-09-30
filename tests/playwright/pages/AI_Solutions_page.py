import os

from pages.base_page import BasePage


class AISolutionsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        self.url = f"{base_url}/en/products/"
        self.heading = page.get_by_role("heading", level=1).first
        self.copilot_card = page.locator("article").filter(
            has=page.get_by_role("heading", name="AI Copilot Development", exact=True)
        )
        self.copilot_brief_link = self.copilot_card.get_by_role(
            "link", name="View solution brief", exact=True
        )

    def load(self):
        self.goto(self.url)

    def is_heading_visible(self):
        return self.heading.is_visible()

    def download_copilot_brief(self):
        with self.page.expect_download() as download_info:
            self.copilot_brief_link.click()
        return download_info.value