from .base_page import BasePage


class ContactPage(BasePage):
    URL = "http://127.0.0.1:8000/contact/"

    def __init__(self, page):
        self.page = page

    def load(self):
        self.goto(self.URL)

    def enter_name(self, name):
        self.page.get_by_role("textbox", name="Name *").click()
        self.page.get_by_role("textbox", name="Name *").fill(name)

    def enter_email(self, email):
        self.page.locator("#email").fill(email)

    def enter_subject(self, subject):
        self.page.locator("#subject").fill(subject)

    def enter_message(self, message):
        self.page.locator("#message").fill(message)

    def send_brief(self):
        self.page.get_by_role("button", name="Send brief").click()

    @property
    def success_message(self):
        return self.page.locator(".alert-success[role='alert']")