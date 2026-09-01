from __future__ import annotations

import requests

import config

REGIONS = ["Americas", "EMEA", "APAC"]
ROLES = ["Employee", "Engineering", "Finance", "Manager"]


class KnowledgeAssistantAPIClient:
    def __init__(self, base_url: str = None, timeout: float = None, session: requests.Session = None):
        self.base_url = (base_url or config.API_BASE_URL).rstrip("/")
        self.timeout = timeout or config.API_TIMEOUT_SECONDS
        self.session = session or requests.Session()

    def _headers(self, region: str = None, role: str = None) -> dict:
        headers = {}
        if region is not None:
            headers["X-User-Region"] = region
        if role is not None:
            headers["X-User-Role"] = role
        return headers

    def query(self, question: str, region: str, role: str) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/query",
            json={"question": question},
            headers=self._headers(region, role),
            timeout=self.timeout,
        )

    def close(self):
        self.session.close()


def extract_answer(payload: dict) -> str:
    for key in ("answer", "response", "text"):
        if key in payload:
            return str(payload[key])
    raise KeyError(f"No answer-like field found in response payload: {list(payload)}")


def extract_citations(payload: dict) -> list[str]:
    for key in ("citations", "citation_ids", "sources"):
        if key in payload:
            raw = payload[key]
            break
    else:
        raise KeyError(f"No citations-like field found in response payload: {list(payload)}")

    ids = []
    for item in raw:
        if isinstance(item, str):
            ids.append(item)
        elif isinstance(item, dict):
            for key in ("id", "doc_id", "document_id"):
                if key in item:
                    ids.append(item[key])
                    break
    return ids


def extract_documents(payload: dict) -> list[dict]:
    for key in ("documents", "docs", "results"):
        if key in payload:
            return payload[key]
    raise KeyError(f"No documents-like field found in response payload: {list(payload)}")


def document_id(document: dict) -> str:
    for key in ("id", "doc_id", "document_id"):
        if key in document:
            return document[key]
    raise KeyError(f"No id-like field found in document: {list(document)}")
