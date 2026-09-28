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