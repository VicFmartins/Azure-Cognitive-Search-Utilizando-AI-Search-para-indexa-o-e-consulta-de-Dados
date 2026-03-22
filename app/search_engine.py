from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from app.models import SearchDocument, SearchHit


TOKEN_RE = re.compile(r"[a-zA-Z0-9_]{2,}")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


class LocalSearchEngine:
    def __init__(self) -> None:
        self.documents: dict[str, SearchDocument] = {}
        self.term_frequencies: dict[str, Counter[str]] = {}
        self.document_frequencies: dict[str, int] = defaultdict(int)
        self.avg_doc_length = 0.0

    def replace_documents(self, documents: list[SearchDocument]) -> None:
        self.documents = {doc.id: doc for doc in documents}
        self._rebuild()

    def add_documents(self, documents: list[SearchDocument]) -> None:
        for doc in documents:
            self.documents[doc.id] = doc
        self._rebuild()

    def _rebuild(self) -> None:
        self.term_frequencies.clear()
        self.document_frequencies.clear()

        total_length = 0
        for doc_id, document in self.documents.items():
            tokens = tokenize(" ".join([document.title, document.category, " ".join(document.tags), document.content]))
            frequencies = Counter(tokens)
            self.term_frequencies[doc_id] = frequencies
            total_length += sum(frequencies.values())
            for term in frequencies:
                self.document_frequencies[term] += 1

        self.avg_doc_length = total_length / len(self.documents) if self.documents else 0.0

    def stats(self) -> tuple[int, int, list[str]]:
        categories = sorted({doc.category for doc in self.documents.values()})
        return len(self.documents), len(self.document_frequencies), categories

    def search(self, query: str, top: int = 5, category: str | None = None, tags: list[str] | None = None) -> list[SearchHit]:
        tags = tags or []
        query_terms = tokenize(query)
        if not query_terms:
            return []

        results: list[SearchHit] = []
        total_docs = max(len(self.documents), 1)

        for doc_id, document in self.documents.items():
            if category and document.category.lower() != category.lower():
                continue
            if tags and not set(tag.lower() for tag in tags).issubset({tag.lower() for tag in document.tags}):
                continue

            frequencies = self.term_frequencies.get(doc_id, Counter())
            doc_length = sum(frequencies.values()) or 1
            score = 0.0
            matched_terms = 0

            for term in query_terms:
                tf = frequencies.get(term, 0)
                if tf == 0:
                    continue
                matched_terms += 1
                df = self.document_frequencies.get(term, 1)
                idf = math.log(1 + ((total_docs - df + 0.5) / (df + 0.5)))
                k1 = 1.5
                b = 0.75
                bm25 = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / max(self.avg_doc_length, 1)))))
                score += bm25

            if matched_terms == 0:
                continue

            title_bonus = sum(1 for term in query_terms if term in tokenize(document.title)) * 0.8
            tag_bonus = sum(1 for term in query_terms if term in [tag.lower() for tag in document.tags]) * 0.5
            semantic_bonus = min(matched_terms / len(query_terms), 1.0) * 1.2
            final_score = round(score + title_bonus + tag_bonus + semantic_bonus, 4)

            results.append(
                SearchHit(
                    id=document.id,
                    title=document.title,
                    category=document.category,
                    tags=document.tags,
                    score=final_score,
                    highlights=self._build_highlights(document.content, query_terms),
                    source=document.source,
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)[:top]

    def get_document(self, doc_id: str) -> SearchDocument | None:
        return self.documents.get(doc_id)

    @staticmethod
    def _build_highlights(content: str, query_terms: list[str], snippet_size: int = 140) -> list[str]:
        lowered = content.lower()
        snippets: list[str] = []
        for term in query_terms:
            index = lowered.find(term.lower())
            if index == -1:
                continue
            start = max(index - 40, 0)
            end = min(index + snippet_size, len(content))
            snippet = content[start:end].strip()
            snippets.append(snippet)
            if len(snippets) == 3:
                break
        return snippets or [content[:snippet_size].strip()]
