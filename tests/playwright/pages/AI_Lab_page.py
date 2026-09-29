import os

from pages.base_page import BasePage


class AILabPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        self.url = f"{base_url}/ai-lab/"
        self.heading = page.get_by_role("heading", name="AI Lab", exact=True)
        self.conversation = page.locator("#chatConversation")
        self.chat_history = page.locator("#chatHistory")
        self.initial_question = page.locator("#initialQuestion")
        self.followup_question = page.locator("#followupQuestion")
        self.start_button = page.locator("#startChatBtn")
        self.ask_button = page.locator("#askBtn")

    def load(self):
        self.goto(self.url)

    def is_heading_visible(self):
        return self.heading.is_visible()

    def select_agent(self, agent):
        self.page.locator(f"label[for='{agent}']").click()

    def is_agent_selected(self, agent):
        return self.page.locator(
            f"input[name='chatAgent'][value='{agent}']"
        ).is_checked()

    def is_agent_selection_disabled(self):
        return self.page.locator("input[name='chatAgent']").first.is_disabled()

    def enter_message(self, message):
        self.initial_question.fill(message)

    def can_start_consultation(self):
        return self.start_button.is_enabled()

    def start_consultation(self):
        self.start_button.click()

    def enter_followup(self, message):
        self.followup_question.fill(message)

    def can_send_followup(self):
        return self.ask_button.is_enabled()

    def send_followup(self):
        self.ask_button.click()

    def wait_for_message(self, message):
        self.chat_history.get_by_text(message, exact=True).wait_for(state="visible")

    def is_conversation_visible(self):
        return self.conversation.is_visible()

    def end_consultation(self):
        self.page.locator("#endChatBtn").click()

    def expect_consultation_ended(self):
        self.conversation.wait_for(state="hidden")
        self.page.locator(".chat-start-composer").wait_for(state="visible")
        assert self.chat_history.locator(".chat-message").count() == 0
        assert not self.is_agent_selection_disabled()