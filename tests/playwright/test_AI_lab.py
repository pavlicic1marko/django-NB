import json

import pytest

from pages.AI_Lab_page import AILabPage


def mock_ai_lab_api(route):
    request = route.request
    payload = request.post_data_json

    if request.url.endswith("/end/"):
        route.fulfill(status=200, content_type="application/json", body="{}")
        return

    if request.url.endswith("/questions/"):
        response = {
            "question": payload["question"],
            "answer": "A useful follow-up response.",
        }
        route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps(response),
        )
        return

    question = payload["question"]
    answer = "Start with a small, measurable workflow."
    qa = {"question": question, "answer": answer}
    response = {
        "thread": {
            "id": 42,
            "agent_type": payload["agent_type"],
            "is_active": True,
            "q_and_as": [qa],
        },
        "q_and_a": qa,
    }
    route.fulfill(
        status=201,
        content_type="application/json",
        body=json.dumps(response),
    )


@pytest.mark.regression
def test_ai_lab_consultation_flow(page):
    page.route("**/api/ai-lab/threads**", mock_ai_lab_api)
    chat = AILabPage(page)
    chat.load()

    assert chat.is_heading_visible()
    assert not chat.can_start_consultation()
    chat.select_agent("gemma3:270m")
    assert chat.is_agent_selected("gemma3:270m")

    chat.enter_message("How can AI help my team?")
    assert chat.can_start_consultation()
    chat.start_consultation()

    chat.wait_for_message("How can AI help my team?")
    chat.wait_for_message("Start with a small, measurable workflow.")
    assert chat.is_conversation_visible()
    assert chat.is_agent_selection_disabled()

    chat.enter_followup("What should we measure first?")
    assert chat.can_send_followup()
    chat.send_followup()
    chat.wait_for_message("What should we measure first?")
    chat.wait_for_message("A useful follow-up response.")

    chat.end_consultation()
    chat.expect_consultation_ended()