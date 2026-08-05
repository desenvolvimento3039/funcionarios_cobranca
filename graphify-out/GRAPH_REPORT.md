# Graph Report - funcionarios_cobranca  (2026-08-05)

## Corpus Check
- 15 files · ~14,994 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 172 nodes · 355 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- app.js
- cobranca_service.py
- processar_substituicoes_job
- cobranca.py
- schemas.py
- post
- Backend Requirements
- alterar_status
- get_psycopg2_conn
- rules/graphify.md
- get_engine
- api.js

## God Nodes (most connected - your core abstractions)
1. `setupEventListeners()` - 34 edges
2. `UI` - 20 edges
3. `carregarCobranca()` - 14 edges
4. `execute_write_dual()` - 13 edges
5. `carregarAnalytics()` - 10 edges
6. `execute_read_dual()` - 9 edges
7. `get_engine()` - 8 edges
8. `CobrancaCreate` - 8 edges
9. `processar_substituicoes_job()` - 8 edges
10. `get_psycopg2_conn()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Docker Service: app` --references--> `Backend Requirements`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `Docker Service: app` --references--> `Frontend Index HTML`  [INFERRED]
  docker-compose.yml → frontend/index.html
- `health_check()` --calls--> `get_psycopg2_conn()`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/core/database.py
- `criar_cobranca()` --references--> `CobrancaCreate`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/models/schemas.py
- `atualizar_cobranca()` --references--> `CobrancaCreate`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/models/schemas.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **System Architecture** — docker_compose_app, backend_requirements, frontend_index [INFERRED 0.80]

## Communities (14 total, 2 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.15
Nodes (39): abrirModalAuditoria(), abrirModalBulkForm(), abrirModalExcel(), abrirModalFilasSemCobrador(), abrirModalItem(), abrirModalSubstitutoDireto(), abrirModalTrocaMassa(), adicionarCobradorFilaCallback() (+31 more)

### Community 1 - "cobranca_service.py"
Cohesion: 0.09
Nodes (37): Any, execute_read_dual(), execute_write_dual(), Executa func(conn) no banco configurado e retorna o resultado., Executa func(conn) em uma transação no banco configurado., alterar_status(), atualizar_cobranca(), atualizar_datas_substituicao() (+29 more)

### Community 2 - "processar_substituicoes_job"
Cohesion: 0.17
Nodes (14): inicializar_schema_bancos(), Garante, de forma idempotente e resiliente a workers concorrentes do Gunicorn,…, cancelar_substituicao_service(), Cancela uma substituição agendada ou em andamento e grava histórico., processar_substituicoes_job(), Job de processamento da tabela fun_cobranca_substituicoes. Atualiza status em…, shutdown_scheduler(), start_scheduler() (+6 more)

### Community 3 - "cobranca.py"
Cohesion: 0.33
Nodes (10): baixar_modelo_excel(), buscar_funcionarios(), estatisticas_analytics(), exportar_csv(), get_filas_sem_cobradores(), health_check(), historico_auditoria(), listar_cobranca() (+2 more)

### Community 4 - "schemas.py"
Cohesion: 0.26
Nodes (11): bulk_update(), criar_substituicao(), criar_substituicao_massa(), BulkUpdateRequest, CobrancaBase, CobrancaCreate, CobrancaResponse, HistoricoSubstituicaoResponse (+3 more)

### Community 5 - "post"
Cohesion: 0.20
Nodes (10): cancelar_substituicao(), criar_cobranca(), deletar_cobranca(), sincronizar_banco(), troca_massa(), upload_excel(), TrocaMassaRequest, delete (+2 more)

### Community 6 - "Backend Requirements"
Cohesion: 0.29
Nodes (7): APScheduler, FastAPI, Backend Requirements, SQLAlchemy, Docker Service: app, Chart.js, Frontend Index HTML

### Community 7 - "alterar_status"
Cohesion: 0.29
Nodes (7): alterar_status(), atualizar_cobranca(), editar_substituicao(), StatusUpdate, SubstituicaoEdit, patch, put

### Community 8 - "get_psycopg2_conn"
Cohesion: 0.25
Nodes (8): debug_db(), Endpoint de diagnóstico detalhado para testar conectividade e inspecionar…, get_psycopg2_conn(), Retorna uma conexão psycopg2 direta ao PostgreSQL., parse_excel_cobranca_bytes(), Lê o Excel de cobrança e retorna lista de tuplas (times_cobranca, num_pa,…, Sincroniza registros de cobrança na tabela fun_funcionarios_cobranca via upsert…, sync_cobranca_rows_to_dbs()

### Community 10 - "get_engine"
Cohesion: 0.21
Nodes (10): garantir_view_roteamento(), get_db(), get_engine(), Alias de compatibilidade., Retorna o engine PostgreSQL configurado., Dependência FastAPI — injeta uma sessão SQLAlchemy., exportar_csv_service(), Gera dados CSV formatados com UTF-8 BOM e delimitador ';' contendo colunas de… (+2 more)

## Knowledge Gaps
- **8 isolated node(s):** `api`, `state`, `graphify`, `Workflow: graphify`, `FastAPI` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_psycopg2_conn()` connect `get_psycopg2_conn` to `get_engine`, `cobranca.py`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `get_engine()` connect `get_engine` to `cobranca_service.py`, `cobranca.py`, `post`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `CobrancaCreate` connect `schemas.py` to `cobranca_service.py`, `cobranca.py`, `post`, `alterar_status`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `setupEventListeners()` (e.g. with `abrirModalAuditoria()` and `abrirModalExcel()`) actually correct?**
  _`setupEventListeners()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `api`, `state`, `graphify` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `cobranca_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09246088193456614 - nodes in this community are weakly interconnected._