from fastapi import FastAPI, HTTPException

from app.azure_payloads import build_azure_index_schema, build_azure_upload_documents_payload
from app.models import IndexDocumentsRequest, IndexStatsResponse, SearchDocument, SearchRequest, SearchResponse
from app.sample_loader import load_sample_documents
from app.search_engine import LocalSearchEngine


app = FastAPI(
    title="Azure AI Search Inspired Demo",
    version="1.0.0",
    description="API local de indexacao e consulta inspirada em Azure AI Search, com payloads prontos para migracao ao servico gerenciado.",
)

engine = LocalSearchEngine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "azure-ai-search-demo"}


@app.post("/api/index/load-sample", response_model=IndexStatsResponse)
def load_sample() -> IndexStatsResponse:
    engine.replace_documents(load_sample_documents())
    documents, unique_terms, categories = engine.stats()
    return IndexStatsResponse(documents=documents, unique_terms=unique_terms, categories=categories)


@app.post("/api/index/documents", response_model=IndexStatsResponse)
def index_documents(payload: IndexDocumentsRequest) -> IndexStatsResponse:
    engine.add_documents(payload.documents)
    documents, unique_terms, categories = engine.stats()
    return IndexStatsResponse(documents=documents, unique_terms=unique_terms, categories=categories)


@app.get("/api/index/stats", response_model=IndexStatsResponse)
def index_stats() -> IndexStatsResponse:
    documents, unique_terms, categories = engine.stats()
    return IndexStatsResponse(documents=documents, unique_terms=unique_terms, categories=categories)


@app.post("/api/search/query", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    hits = engine.search(
        query=payload.query,
        top=payload.top,
        category=payload.category,
        tags=payload.tags,
    )
    return SearchResponse(query=payload.query, total_hits=len(hits), hits=hits)


@app.get("/api/documents/{doc_id}", response_model=SearchDocument)
def get_document(doc_id: str) -> SearchDocument:
    document = engine.get_document(doc_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.")
    return document


@app.get("/api/azure/index-schema")
def azure_index_schema() -> dict:
    return build_azure_index_schema()


@app.get("/api/azure/upload-payload")
def azure_upload_payload() -> dict:
    documents = list(engine.documents.values()) or load_sample_documents()
    return build_azure_upload_documents_payload(documents)
