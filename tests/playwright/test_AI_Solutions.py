import pytest

from pages.AI_Solutions_page import AISolutionsPage


@pytest.mark.regression
def test_download_ai_copilot_development_brief(page):
	ai_solutions = AISolutionsPage(page)
	ai_solutions.load()

	assert ai_solutions.is_heading_visible()
	download = ai_solutions.download_copilot_brief()

	assert download.suggested_filename == "ai-copilot-development-brief.pdf"
