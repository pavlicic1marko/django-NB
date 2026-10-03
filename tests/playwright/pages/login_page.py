from .base_page import BasePage


class LoginPage(BasePage):
    URL = "http://127.0.0.1:8000/login/"

    def __init__(self, page):
        super().__init__(page)
        self.login_button = page.locator('button[type="submit"]', has_text="Log in")
        self.register_button = page.get_by_role("link", name="Register")

    def load(self):
        self.goto(self.URL)

    def is_login_button_visible(self):
        return self.login_button.is_visible()

    def click_register(self):
        self.register_button.click()
