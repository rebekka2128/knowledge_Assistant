import pytest
from utils.validators_api import validate_query_response


def test_golden_question_api(api_client, api_golden_question):

    golden_question = api_golden_question

    response = api_client.query(
        question=golden_question["question"],
        region=golden_question["region"],
        role=golden_question["role"],
    )

    expected_status = golden_question["expected_status"]

    assert response.status_code == expected_status, (
        f"[{golden_question['id']}] "
        f"Expected HTTP {expected_status}, "
        f"got {response.status_code}: {response.text}"
    )

    validate_query_response(
        payload=response.json(),
        scenario=golden_question
    )


@pytest.mark.parametrize("region", ["Americas", "EMEA", "APAC"])
@pytest.mark.parametrize("role", ["Employee", "Engineering", "Finance", "Manager"])
def test_query_requires_region_and_role_headers(api_client, region, role):
    response = api_client.query(
        question="What is my daily meal allowance when I travel?",
        region=region,
        role=role,
    )
    print(f"\n[region] {region}")
    print(f"\n[role] {role}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 200, (
        f"{region}/{role}: expected 200 OK, got {response.status_code}: {response.text}"
    )


@pytest.mark.parametrize("missing_header", ["region", "role"], ids=["missing_region", "missing_role"])
def test_query_missing_context_header(api_client, missing_header):
    region = None if missing_header == "region" else "Americas"
    role = None if missing_header == "role" else "Employee"

    response = api_client.query(
        question="What is my daily meal allowance when I travel?",
        region=region,
        role=role,
    )
    print(f"\n[INVALID {missing_header.upper()}] {missing_header}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code < 500, (
        f"Missing {missing_header} header caused a server error: "
        f"{response.status_code}: {response.text}"
    )