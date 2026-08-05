# Graph Report - funcionarios_cobranca  (2026-08-04)

## Corpus Check
- 15 files · ~10,226 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 149 nodes · 296 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.54)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a83cea2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.js
- get_engine
- cobranca.py
- cobranca_service.py
- Infrastructure and Dependencies
- sync_service.py
- Graphify Workflow Rules
- Frontend API Integration

## God Nodes (most connected - your core abstractions)
1. `setupEventListeners()` - 27 edges
2. `UI` - 15 edges
3. `execute_write_dual()` - 13 edges
4. `get_engine()` - 12 edges
5. `carregarCobranca()` - 11 edges
6. `execute_read_dual()` - 10 edges
7. `CobrancaCreate` - 8 edges
8. `garantir_view_roteamento()` - 7 edges
9. `carregarAnalytics()` - 7 edges
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

## Communities (10 total, 2 thin omitted)

### Community 0 - "app.js"
Cohesion: 0.17
Nodes (32): abrirModalAuditoria(), abrirModalBulkForm(), abrirModalFilasSemCobrador(), abrirModalItem(), abrirModalSubstitutoDireto(), abrirModalTrocaMassa(), adicionarCobradorFilaCallback(), alternarStatus() (+24 more)

### Community 1 - "get_engine"
Cohesion: 0.13
Nodes (19): garantir_view_roteamento(), get_db(), get_engine(), Garante a criação da View SQL vw_cobranca_roteamento para leitura pela…, Dependência para injeção de sessão do SQLAlchemy no FastAPI., exportar_csv_service(), Gera dados CSV formatados com delimitador ';'., processar_substituicoes_job() (+11 more)

### Community 2 - "cobranca.py"
Cohesion: 0.11
Nodes (35): alterar_status(), atualizar_cobranca(), bulk_update(), buscar_funcionarios(), criar_cobranca(), criar_substituicao(), deletar_cobranca(), editar_substituicao() (+27 more)

### Community 3 - "cobranca_service.py"
Cohesion: 0.10
Nodes (33): Any, execute_read_dual(), execute_write_dual(), Executa uma função de leitura no primeiro banco funcional., Executa uma função de escrita nos bancos., alterar_status(), atualizar_cobranca(), atualizar_datas_substituicao() (+25 more)

### Community 9 - "Infrastructure and Dependencies"
Cohesion: 0.29
Nodes (7): APScheduler, FastAPI, Backend Requirements, SQLAlchemy, Docker Service: app, Chart.js, Frontend Index HTML

### Community 12 - "sync_service.py"
Cohesion: 0.40
Nodes (4): parse_excel_cobranca_bytes(), Sincroniza registros de cobrança na tabela fun_funcionarios_cobranca via upsert., Lê o Excel de cobrança e retorna lista de tuplas (times_cobranca, num_pa,…, sync_cobranca_rows_to_dbs()

## Knowledge Gaps
- **8 isolated node(s):** `api`, `state`, `graphify`, `Workflow: graphify`, `FastAPI` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_engine()` connect `get_engine` to `cobranca.py`, `cobranca_service.py`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `execute_write_dual()` connect `cobranca_service.py` to `get_engine`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `get_psycopg2_conn()` connect `cobranca.py` to `get_engine`, `sync_service.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `setupEventListeners()` (e.g. with `abrirModalAuditoria()` and `abrirModalFilasSemCobrador()`) actually correct?**
  _`setupEventListeners()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `api`, `state`, `graphify` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `get_engine` be split into smaller, more focused modules?**
  _Cohesion score 0.13438735177865613 - nodes in this community are weakly interconnected._
- **Should `cobranca.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10960960960960961 - nodes in this community are weakly interconnected._