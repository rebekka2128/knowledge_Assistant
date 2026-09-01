import json

import pytest
from utils.validators_knowledgeAssistant import validate_knowledge_assistant_response


@pytest.mark.parametrize("region", ["Americas", "EMEA", "APAC"])
def test_select_region(knowledge_assistant_page, region):
    knowledge_assistant_page.select_region(region)
    selected = knowledge_assistant_page.get_selected_region()
    assert selected.lower() == region.lower()


@pytest.mark.parametrize("role", ["Employee", "Engineering", "Finance", "Manager"])
def test_select_role(knowledge_assistant_page, role):
    knowledge_assistant_page.select_role(role)
    selected = knowledge_assistant_page.get_selected_role()
    assert selected.lower() == role.lower()


def test_golden_question_ui(knowledge_assistant_page, ui_golden_question):

    golden_question = ui_golden_question

    knowledge_assistant_page.select_region(golden_question["region"])
    knowledge_assistant_page.select_role(golden_question["role"])
    knowledge_assistant_page.ask_question(golden_question["question"])

    results = knowledge_assistant_page.get_results()

    answer = results["answer"]
    citations = results["citations"]
    visible_documents = results["visible_documents"]

    validate_knowledge_assistant_response(
        answer=answer,
        citations=citations,
        visible_documents=visible_documents,
        scenario=golden_question
    )

    print("\n========== ACTUAL RESULT ==========")
    print(f"Test Case: {golden_question['id']}")
    print(f"Answer: {answer}")
    print(f"Citations: {citations}")
    print(f"Visible Documents: {visible_documents}")
    print("===================================\n")