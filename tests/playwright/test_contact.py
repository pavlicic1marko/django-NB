import pytest

from pages.contact_page import ContactPage


@pytest.mark.regression
def test_contact_page_send_message(page):
    contact = ContactPage(page)
    contact.load()

    contact.enter_name("Test User")
    contact.enter_email("test@example.com")
    contact.enter_subject("Playwright test")
    contact.enter_message("Please contact me about your AI services.")
    contact.send_brief()

    assert contact.success_message.inner_text().strip()