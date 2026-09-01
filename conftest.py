import json
import config
import pytest
from playwright.sync_api import sync_playwright
from pages.knowledge_Assistant import KnowledgeAssistant
from utils.api_client import KnowledgeAssistantAPIClient


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=config.HEADLESS,
            slow_mo=config.SLOW_MO,
        )
        context = browser.new_context(
            viewport={"width": 1512, "height": 982}
        )
        page = context.new_page()

        yield page
        page.close()
        context.close()
        browser.close()

@pytest.fixture
def knowledge_assistant_page(page):
    return KnowledgeAssistant(page).open()

@pytest.fixture
def api_client():
    client = KnowledgeAssistantAPIClient()
    yield client
    client.close()

def load_golden_questions():
    with open("test_data/golden_questions.json", "r") as file:
        return json.load(file)

@pytest.fixture(
    params=[
        question
        for question in load_golden_questions()
        if "ui" in question.get("test_type", [])
    ],
    ids=lambda question: question["id"]
)
def ui_golden_question(request):
    return request.param


@pytest.fixture(
    params=[
        question
        for question in load_golden_questions()
        if "api" in question.get("test_type", [])
    ],
    ids=lambda question: question["id"]
)
def api_golden_question(request):
    return request.param