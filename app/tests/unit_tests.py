import sys
import os
import pytest
from pydantic import BaseModel
from fastapi.testclient import TestClient

# Ensure the project root is on PYTHONPATH so `main` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.utils.LLM import LLMClient
from app.nodes.classification import classify_input_node


# Dummy classification model for testing
class DummyClassification(BaseModel):
    classification: str
    confidence_score: float


# Dummy Bug Report Model for testing
class DummyBugReport(BaseModel):
    title: str
    reproduction_steps: list[str]
    affected_components: list[str]


# Fixture to mock the LLMClient's `parse` method
@pytest.fixture(autouse=True)
def patch_llm(monkeypatch):
    """Always return a predictable model from LLMClient.parse"""

    def fake_parse(*args, **kwargs):
        # Ensure that the 'messages' argument is passed in correctly
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", None)
        response_format = kwargs.get("response_format", None)

        print(
            f"Messages: {messages}, Model: {model}, Response Format: {response_format}"
        )

        # If it's a classification request, mock classification result
        if "classification" in messages[1]["content"]:
            return DummyClassification(
                classification="bug_report", confidence_score=0.99
            )

        # If it's a bug report extraction request, mock bug report details
        if "bug report" in messages[1]["content"]:
            return DummyBugReport(
                title="Login Issue",
                reproduction_steps=["Enter credentials", "Click login"],
                affected_components=["Authentication Module", "UI"],
            )

        return DummyClassification(
            classification="general_inquiry", confidence_score=0.5
        )

    # Correctly patch the 'parse' method with a mock
    monkeypatch.setattr(LLMClient, "parse", fake_parse)


@pytest.mark.asyncio
async def test_classify_node():
    state = {
        "message": "I can't log in to the application",
        "customer_id": "u1",
        "product": "MobileApp",
    }

    # Await the result of the coroutine function
    result = await classify_input_node(state)
    print(result)
    # Assert the expected output
    assert result["classification"] == "bug_report"
    assert result["confidence_score"] == pytest.approx(0.99)


def test_endpoint_happy_path():
    payload = {
        "customer_id": "u1",
        "message": "I can't log in to the application",
        "product": "MobileApp",
    }

    # Use FastAPI TestClient for the endpoint test
    with TestClient(app) as client:
        response = client.post("/process-customer-message", json=payload)
    print(response)
    assert response.status_code == 200
    body = response.json()
    assert body["message_type"] == "bug_report"
    assert "ticket" in body["response_data"]
    assert "customer_response" in body


def test_invalid_product():
    payload = {"customer_id": "u1", "message": "Test", "product": "NotARealProduct"}

    # Use FastAPI TestClient for the endpoint test
    with TestClient(app) as client:
        response = client.post("/process-customer-message", json=payload)

    assert response.status_code == 200
    assert response.json()["customer_response"] == "Invalid Product Name"


def test_deterministic_output():
    payload = {
        "customer_id": "u1",
        "message": "I can't log in to the application",
        "product": "MobileApp",
    }

    responses = []

    with TestClient(app) as client:
        for _ in range(5):
            response = client.post("/process-customer-message", json=payload)
            assert response.status_code == 200
            data = response.json()

            data.pop("customer_response", None)

            if "ticket" in data["response_data"]:
                ticket = data["response_data"]["ticket"]
                ticket_without_id = {k: v for k, v in ticket.items() if (k != "id")}
                data["response_data"]["ticket"] = ticket_without_id

            responses.append(data)
            print()

    for result in responses[1:]:
        assert result == responses[0], (
            f"Inconsistent output: {result} != {responses[0]}"
        )
