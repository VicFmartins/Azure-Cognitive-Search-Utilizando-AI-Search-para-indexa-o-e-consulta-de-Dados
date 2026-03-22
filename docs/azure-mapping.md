# Mapeamento para Azure AI Search

Este projeto roda localmente, mas foi desenhado para espelhar conceitos reais do Azure AI Search.

## Conceitos equivalentes

- `data/sample_documents.json` -> fonte de dados
- `app/search_engine.py` -> logica local de indexacao e ranking
- `/api/azure/index-schema` -> payload de criacao de indice
- `/api/azure/upload-payload` -> payload de upload de documentos
- `category` e `tags` -> filtros e facetas
- `title`, `content` e `tags` -> campos priorizados para busca

## O que o Azure adicionaria

- servico gerenciado e escalavel
- indexadores e skillsets
- enriquecimento de IA
- semantic ranker
- filtros, facets e scoring profiles em nivel de plataforma

## Uso como portfolio

O demo local ajuda a mostrar:

- modelagem de indice
- pipeline de ingestao
- experiencia de consulta
- preparo para migracao ao Azure AI Search
