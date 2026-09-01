def validate_knowledge_assistant_response(answer, citations, visible_documents, scenario):
    expected_behavior = scenario["expected_behavior"]
    expected_facts = scenario.get("expected_facts", [])
    expected_citations = scenario.get("expected_citations", [])
    forbidden_citations = scenario.get("forbidden_citations", [])
    expected_visible_documents = scenario.get("expected_visible_documents", [])

    normalized_answer = answer.lower().strip()
    normalized_citations = [
        str(citation).upper().strip()
        for citation in citations
    ]
    normalized_visible_documents = [
        str(document).upper().strip()
        for document in visible_documents
    ]

    assert normalized_answer, ("Assistant returned an empty answer.")

    if expected_behavior == "answer":

        for fact in expected_facts:
            assert fact.lower() in normalized_answer, (
                f"Expected fact not found: '{fact}'\n"
                f"Actual answer: {answer}"
            )

    elif expected_behavior == "refusal":

        for fact in expected_facts:
            assert fact.lower() not in normalized_answer, (
                f"Restricted fact was exposed: '{fact}'\n"
                f"Actual answer: {answer}"
            )

    else:
        raise AssertionError(
            f"Unsupported expected behavior: {expected_behavior}"
        )

    #validate expected citations
    for citation in expected_citations:

        assert citation.upper() in normalized_citations, (
            f"Expected citation '{citation}' was not found.\n"
            f"Actual citations: {normalized_citations}"
        )

    #validate forbidden citations
    for citation in forbidden_citations:
        assert citation.upper() not in normalized_citations, (
            f"Forbidden citation '{citation}' was found in citations.\n"
            f"Actual citations: {normalized_citations}"
        )
        assert citation.lower() not in normalized_answer, (
            f"Forbidden citation '{citation}' was mentioned in the answer text.\n"
            f"Actual answer: {answer}"
        )

    #validate visible documents
    for document in expected_visible_documents:
        assert any(
            document.upper() in visible_doc.upper()
            for visible_doc in normalized_visible_documents
        ), (
            f"Expected visible document '{document}' was not found.\n"
            f"Actual visible documents: {normalized_visible_documents}"
        )