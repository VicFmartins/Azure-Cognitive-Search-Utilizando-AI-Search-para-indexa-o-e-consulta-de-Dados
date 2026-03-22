from __future__ import annotations

from app.models import SearchDocument


def build_azure_index_schema() -> dict:
    return {
        "name": "technical-articles-index",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "searchable": False, "filterable": True, "sortable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": True},
            {"name": "category", "type": "Edm.String", "searchable": True, "filterable": True, "facetable": True, "sortable": True},
            {"name": "tags", "type": "Collection(Edm.String)", "searchable": True, "filterable": True, "facetable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "source", "type": "Edm.String", "searchable": False, "filterable": True, "sortable": True},
        ],
        "semantic": {
            "configurations": [
                {
                    "name": "default-semantic-config",
                    "prioritizedFields": {
                        "titleField": {"fieldName": "title"},
                        "prioritizedContentFields": [{"fieldName": "content"}],
                        "prioritizedKeywordsFields": [{"fieldName": "tags"}],
                    },
                }
            ]
        },
    }


def build_azure_upload_documents_payload(documents: list[SearchDocument]) -> dict:
    return {
        "value": [
            {
                "@search.action": "mergeOrUpload",
                "id": doc.id,
                "title": doc.title,
                "category": doc.category,
                "tags": doc.tags,
                "content": doc.content,
                "source": doc.source,
            }
            for doc in documents
        ]
    }
