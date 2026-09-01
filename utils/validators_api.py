from utils.api_client import extract_answer, extract_citations


def validate_query_response(payload: dict, scenario: dict):
    expected_behavior = scenario["expected_behavior"]
    expected_facts = scenario.get("expected_facts", [])
    expected_citations = scenario.get("expected_citations", [])
    forbidden_citations = scenario.get("forbidden_citations", [])

    answer = extract_answer(payload)
    citations = extract_citations(payload)

    normalized_answer = answer.lower().strip()
    normalized_citations = [str(c).upper().strip() for c in citations]

    assert normalized_answer, "Assistant returned an empty answer."

    if expected_behavior == "answer":
        for fact in expected_facts:
            assert fact.lower() in normalized_answer, (
                f"Expected fact not found: '{fact}'\nActual answer: {answer}"
            )
    elif expected_behavior == "refusal":
        for fact in expected_facts:
            assert fact.lower() not in normalized_answer, (
                f"Restricted fact was exposed: '{fact}'\nActual answer: {answer}"
            )
    else:
        raise AssertionError(f"Unsupported expected behavior: {expected_behavior}")

    for citation in expected_citations:
        assert citation.upper() in normalized_citations, (
            f"Expected citation '{citation}' was not found.\nActual citations: {normalized_citations}"
        )

    for citation in forbidden_citations:
        assert citation.upper() not in normalized_citations, (
            f"Forbidden citation '{citation}' was found in citations.\nActual citations: {normalized_citations}"
        )
        assert citation.lower() not in normalized_answer, (
            f"Forbidden citation '{citation}' was mentioned in the answer text.\nActual answer: {answer}"
        )
