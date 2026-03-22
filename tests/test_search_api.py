from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_load_sample_documents_builds_index() -> None:
    response = client.post("/api/index/load-sample")

    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == 5
    assert "search" in data["categories"]


def test_search_returns_ranked_results() -> None:
    client.post("/api/index/load-sample")
    response = client.post(
        "/api/search/query",
        json={"query": "semantic search relevance", "top": 3, "category": "search"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] >= 1
    assert data["hits"][0]["category"] == "search"
    assert "Semantic Search Basics" in data["hits"][0]["title"]


def test_search_with_tags_filters_results() -> None:
    client.post("/api/index/load-sample")
    response = client.post(
        "/api/search/query",
        json={"query": "azure indexing", "top": 5, "tags": ["documents"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] == 1
    assert data["hits"][0]["id"] == "doc-003"


def test_azure_payload_endpoints_return_schema_and_documents() -> None:
    client.post("/api/index/load-sample")

    schema_response = client.get("/api/azure/index-schema")
    payload_response = client.get("/api/azure/upload-payload")

    assert schema_response.status_code == 200
    assert payload_response.status_code == 200
    assert schema_response.json()["name"] == "technical-articles-index"
    assert len(payload_response.json()["value"]) == 5
