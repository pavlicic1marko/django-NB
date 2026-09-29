import pytest

from pages.AI_Lab_page import AILabPage


@pytest.mark.test
def test_contact_page_send_message(page):
    chat = AILabPage(page)
    chat.load()

    chat.select_agent("gemma3@270m")
    chat.enter_message("Answer with just test")
    chat.start_consultation()

    chat.wait_for_answer()
    chat.end_consultation()
    chat.expect_consultation_ended()