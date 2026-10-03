from .base_page import BasePage

class HomePage(BasePage):
    URL = "http://127.0.0.1:8000/"
    HEADING_TEXT = "We build AI products and integrations that move your business faster."

    HEADING_TEXT_DE = "Wir entwickeln KI-Produkte und Integrationen, die Ihr Unternehmen schneller voranbringen."

    def __init__(self, page):
        super().__init__(page)
        self.heading = page.locator("h1", has_text=self.HEADING_TEXT)
        self.heading_any = page.locator("h1")
        self.favicon = page.locator('link[rel="icon"]')
        self.language_summary = page.locator(".language-summary")
        self.language_code = page.locator(".language-summary .code")
        self.language_flag = page.locator(".language-summary .flag")
        self.language_menu_de_link = page.locator(".language-menu a", has_text="Deutsch")
        self.profile_button = page.locator(".profile-button")
        self.login_link = page.locator(".profile-menu a", has_text="Log in")
        self.register_link = page.locator(".profile-menu a", has_text="Register")

    def load(self):
        self.goto(self.URL)

    def open_profile_menu(self):
        self.profile_button.click()

    def click_login(self):
        self.login_link.click()

    def click_register(self):
        self.register_link.click()

    def switch_language_to_de(self):
        self.language_summary.click()
        self.language_menu_de_link.click()

    def get_language_code(self):
        return self.language_code.text_content()

    def get_language_flag_src(self):
        return self.language_flag.get_attribute("src")

    def is_heading_visible(self):
        return self.heading.is_visible()

    def get_heading_text(self):
        heading_text = self.heading_any.text_content()
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