import gettext
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "locale" / "de" / "LC_MESSAGES" / "django.mo"


def test_german_registration_and_ai_lab_translations():
    translation = gettext.translation("django", localedir=CATALOG.parents[2], languages=["de"])

    expected = {
        "AI Lab | AI Solutions Studio": "KI-Labor | AI Solutions Studio",
        "AI Lab": "KI-Labor",
        "Connect with a specialized assistant for AI strategy, integrations, or implementation planning. Choose the assistant that matches your goal, then type your question to get started.": "Verbinden Sie sich mit einem spezialisierten Assistenten für KI-Strategie, Integrationen oder Implementierungsplanung. Wählen Sie den Assistenten aus, der zu Ihrem Ziel passt, und geben Sie dann Ihre Frage ein.",
        "Create an account": "Konto erstellen",
        "Create account": "Konto erstellen",
        "Local LLM": "Lokales LLM",
        "Cloud LLM": "Cloud-LLM",
        "Image Analysis": "Bildanalyse",
        "Choose an AI agent": "KI-Agent auswählen",
        "Size: 92 MB": "Größe: 92 MB",
        "Size: 1.3 GB": "Größe: 1,3 GB",
        "Size: 292 MB": "Größe: 292 MB",
        "Ask about your AI goals": "Fragen Sie nach Ihren KI-Zielen",
        "Describe your AI project or integration challenge...": "Beschreiben Sie Ihr KI-Projekt oder Ihre Integrationsherausforderung...",
        "Please enter a question before starting the AI chat.": "Bitte geben Sie eine Frage ein, bevor Sie den KI-Chat starten.",
        "Start AI consultation": "KI-Beratung starten",
        "Processing...": "Verarbeitung...",
        "End chat": "Chat beenden",
        "END CHAT": "CHAT BEENDEN",
        "Ask a follow-up about architecture, models, or rollout...": "Stellen Sie eine Rückfrage zu Architektur, Modellen oder Rollout...",
        "Coming soon.": "Demnächst verfügbar.",
        "Ask about an image": "Stellen Sie eine Frage zu einem Bild",
        "Image (maximum 11 KB)": "Bild (maximal 11 KB)",
        "Choose file": "Datei auswählen",
        "No file chosen": "Keine Datei ausgewählt",
        "Upload an image no larger than 11 KB.": "Laden Sie ein Bild mit höchstens 11 KB hoch.",
        "Your question": "Ihre Frage",
        "Ask": "Fragen",
        "Analyzing...": "Wird analysiert...",
        "Answer": "Antwort",
        "Image must be 11 KB or smaller.": "Das Bild darf höchstens 11 KB groß sein.",
    }

    assert {message: translation.gettext(message) for message in expected} == expected
