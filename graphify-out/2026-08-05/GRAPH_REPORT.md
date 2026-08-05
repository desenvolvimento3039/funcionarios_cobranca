# Graph Report - .  (2026-08-05)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 172 nodes · 350 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- app.js
- cobranca_service.py
- get_engine
- cobranca.py
- schemas.py
- post
- Backend Requirements
- alterar_status
- sync_service.py
- rules/graphify.md
- CobrancaCreate
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
9. `get_psycopg2_conn()` - 7 edges
10. `TrocaMassaRequest` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Docker Service: app` --references--> `Backend Requirements`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `Docker Service: app` --references--> `Frontend Index HTML`  [INFERRED]
  docker-compose.yml → frontend/index.html
- `sincronizar_banco()` --calls--> `get_engine()`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/core/database.py
- `sync_cobranca_rows_to_dbs()` --calls--> `get_psycopg2_conn()`  [EXTRACTED]
  backend/app/services/sync_service.py → backend/app/core/database.py
- `atualizar_cobranca()` --references--> `CobrancaCreate`  [EXTRACTED]
  backend/app/services/cobranca_service.py → backend/app/models/schemas.py

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
Nodes (39): Any, execute_read_dual(), execute_write_dual(), Executa func(conn) no banco configurado e retorna o resultado., Executa func(conn) em uma transação no banco configurado., alterar_status(), atualizar_cobranca(), atualizar_datas_substituicao() (+31 more)

### Community 2 - "get_engine"
Cohesion: 0.11
Nodes (22): garantir_view_roteamento(), get_db(), get_engine(), inicializar_schema_bancos(), Alias de compatibilidade., Retorna o engine PostgreSQL configurado., Dependência FastAPI — injeta uma sessão SQLAlchemy., Garante, de forma idempotente e resiliente a workers concorrentes do Gunicorn,… (+14 more)

### Community 3 - "cobranca.py"
Cohesion: 0.24
Nodes (14): baixar_modelo_excel(), buscar_funcionarios(), debug_db(), estatisticas_analytics(), exportar_csv(), get_filas_sem_cobradores(), health_check(), historico_auditoria() (+6 more)

### Community 4 - "schemas.py"
Cohesion: 0.27
Nodes (10): bulk_update(), criar_substituicao(), troca_massa(), BulkUpdateRequest, CobrancaBase, CobrancaResponse, HistoricoSubstituicaoResponse, SubstituicaoDirectCreate (+2 more)

### Community 5 - "post"
Cohesion: 0.22
Nodes (9): cancelar_substituicao(), criar_substituicao_massa(), deletar_cobranca(), sincronizar_banco(), upload_excel(), SubstituicaoMassaRequest, delete, post (+1 more)

### Community 6 - "Backend Requirements"
Cohesion: 0.29
Nodes (7): APScheduler, FastAPI, Backend Requirements, SQLAlchemy, Docker Service: app, Chart.js, Frontend Index HTML

### Community 7 - "alterar_status"
Cohesion: 0.33
Nodes (6): alterar_status(), editar_substituicao(), StatusUpdate, SubstituicaoEdit, patch, put

### Community 8 - "sync_service.py"
Cohesion: 0.40
Nodes (4): parse_excel_cobranca_bytes(), Lê o Excel de cobrança e retorna lista de tuplas (times_cobranca, num_pa,…, Sincroniza registros de cobrança na tabela fun_funcionarios_cobranca via upsert…, sync_cobranca_rows_to_dbs()

### Community 10 - "CobrancaCreate"
Cohesion: 0.67
Nodes (3): atualizar_cobranca(), criar_cobranca(), CobrancaCreate

## Knowledge Gaps
- **8 isolated node(s):** `graphify`, `Workflow: graphify`, `FastAPI`, `SQLAlchemy`, `APScheduler` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_psycopg2_conn()` connect `cobranca.py` to `sync_service.py`, `get_engine`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `get_engine()` connect `get_engine` to `cobranca_service.py`, `cobranca.py`, `post`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `execute_write_dual()` connect `cobranca_service.py` to `get_engine`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `setupEventListeners()` (e.g. with `abrirModalAuditoria()` and `abrirModalExcel()`) actually correct?**
  _`setupEventListeners()` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `graphify`, `Workflow: graphify`, `FastAPI` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `cobranca_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08717948717948718 - nodes in this community are weakly interconnected._
- **Should `get_engine` be split into smaller, more focused modules?**
  _Cohesion score 0.1076923076923077 - nodes in this community are weakly interconnected._