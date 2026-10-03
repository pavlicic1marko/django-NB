from .base_page import BasePage


class RegisterPage(BasePage):
    URL = "http://127.0.0.1:8000/register/"

    def __init__(self, page):
        super().__init__(page)
        self.create_account_button = page.locator('button[type="submit"]', has_text="Create account")

    def load(self):
        self.goto(self.URL)

    def is_create_account_button_visible(self):
        return self.create_account_button.is_visible()
