# Graph Report - .  (2026-08-03)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 124 nodes · 217 edges · 18 communities (16 shown, 2 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.56)
- Token cost: 874 input · 182 output

## Graph Freshness
- Built from commit: `a83cea2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Frontend UI Logic
- Background Scheduler and Lifecycle
- Data Retrieval Functions
- Employee Management Logic
- Data Validation Schemas
- Read-Only Analytics Queries
- Resource Creation Endpoints
- Dual-Write Database Logic
- Core Business Services
- Infrastructure and Dependencies
- Update API Endpoints
- Database Session Management
- Excel Data Synchronization
- Graphify Workflow Rules
- Frontend API Integration
- Resource Deletion Endpoints

## God Nodes (most connected - your core abstractions)
1. `setupEventListeners()` - 16 edges
2. `get_engine()` - 10 edges
3. `execute_write_dual()` - 10 edges
4. `execute_read_dual()` - 9 edges
5. `UI` - 9 edges
6. `carregarCobranca()` - 8 edges
7. `salvarItem()` - 6 edges
8. `salvarSubstitutoDireto()` - 6 edges
9. `CobrancaCreate` - 5 edges
10. `get_psycopg2_conn()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Docker Service: app` --references--> `Backend Requirements`  [INFERRED]
  docker-compose.yml → backend/requirements.txt
- `Docker Service: app` --references--> `Frontend Index HTML`  [INFERRED]
  docker-compose.yml → frontend/index.html
- `criar_cobranca()` --references--> `CobrancaCreate`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/models/schemas.py
- `atualizar_cobranca()` --references--> `CobrancaCreate`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/models/schemas.py
- `sincronizar_banco()` --calls--> `get_engine()`  [EXTRACTED]
  backend/app/api/cobranca.py → backend/app/core/database.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **System Architecture** — docker_compose_app, backend_requirements, frontend_index [INFERRED 0.80]

## Communities (18 total, 2 thin omitted)

### Community 0 - "Frontend UI Logic"
Cohesion: 0.23
Nodes (20): abrirModalFilasSemCobrador(), abrirModalItem(), abrirModalSubstitutoDireto(), adicionarCobradorFilaCallback(), alternarStatus(), carregarAnalytics(), carregarCobranca(), confirmarExclusao() (+12 more)

### Community 1 - "Background Scheduler and Lifecycle"
Cohesion: 0.24
Nodes (10): processar_substituicoes_job(), Job diário que lê a tabela fun_cobranca_substituicoes e atualiza os status na…, shutdown_scheduler(), start_scheduler(), allow_iframe_middleware(), lifespan(), get, read_root() (+2 more)

### Community 2 - "Data Retrieval Functions"
Cohesion: 0.36
Nodes (9): buscar_funcionarios(), estatisticas_analytics(), exportar_csv(), get_filas_sem_cobradores(), health_check(), listar_cobranca(), listar_pas(), get (+1 more)

### Community 3 - "Employee Management Logic"
Cohesion: 0.22
Nodes (9): Any, alterar_status(), atualizar_datas_substituicao(), buscar_funcionarios(), listar_pas(), Alterna o status de um funcionário (1: Ativo, 0: Inativo)., Busca dinâmica de funcionários por nome ou matrícula., Atualiza período agendado de substituição. (+1 more)

### Community 4 - "Data Validation Schemas"
Cohesion: 0.39
Nodes (7): editar_substituicao(), CobrancaBase, CobrancaCreate, CobrancaResponse, HistoricoSubstituicaoResponse, SubstituicaoEdit, BaseModel

### Community 5 - "Read-Only Analytics Queries"
Cohesion: 0.25
Nodes (8): execute_read_dual(), Executa uma função de leitura no primeiro banco funcional (SicoobSMO -> LeCom)., estatisticas_analytics(), listar_cobranca(), listar_filas_sem_cobradores(), Localiza filas em inadimplência sem nenhum cobrador ativo associado., Compila relatórios analíticos de funcionários por time, PA e status., Lista funcionários de cobrança com suporte a paginação, filtros e ordenação.

### Community 6 - "Resource Creation Endpoints"
Cohesion: 0.29
Nodes (7): criar_cobranca(), criar_substituicao(), sincronizar_banco(), upload_excel(), SubstituicaoDirectCreate, post, UploadFile

### Community 7 - "Dual-Write Database Logic"
Cohesion: 0.33
Nodes (7): execute_write_dual(), Executa uma função de escrita em ambos os bancos (SicoobSMO e LeCom)., atualizar_cobranca(), criar_cobranca(), Cria um novo funcionário de cobrança nos bancos de dados., Atualiza dados cadastrais do funcionário de cobrança., CobrancaCreate

### Community 8 - "Core Business Services"
Cohesion: 0.29
Nodes (6): criar_substituicao_direta(), deletar_cobranca(), exportar_csv_service(), Exclui um funcionário de cobrança pelo ID., Gera dados CSV formatados com delimitador ';'., Agenda uma nova substituição direta entre dois cobradores.

### Community 9 - "Infrastructure and Dependencies"
Cohesion: 0.29
Nodes (7): APScheduler, FastAPI, Backend Requirements, SQLAlchemy, Docker Service: app, Chart.js, Frontend Index HTML

### Community 10 - "Update API Endpoints"
Cohesion: 0.40
Nodes (5): alterar_status(), atualizar_cobranca(), StatusUpdate, patch, put

### Community 11 - "Database Session Management"
Cohesion: 0.50
Nodes (4): get_db(), get_engine(), Dependência para injeção de sessão do SQLAlchemy no FastAPI., Session

### Community 12 - "Excel Data Synchronization"
Cohesion: 0.40
Nodes (4): parse_excel_cobranca_bytes(), Sincroniza registros de cobrança na tabela fun_funcionarios_cobranca via upsert., Lê o Excel de cobrança e retorna lista de tuplas (times_cobranca, num_pa,…, sync_cobranca_rows_to_dbs()

### Community 13 - "Graphify Workflow Rules"
Cohesion: 0.50
Nodes (4): Graphify Rules, graphify, Graphify Workflow, Workflow: graphify

## Knowledge Gaps
- **8 isolated node(s):** `api`, `graphify`, `Workflow: graphify`, `state`, `FastAPI` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_engine()` connect `Database Session Management` to `Background Scheduler and Lifecycle`, `Data Retrieval Functions`, `Read-Only Analytics Queries`, `Resource Creation Endpoints`, `Dual-Write Database Logic`, `Core Business Services`?**
  _High betweenness centrality (0.227) - this node is a cross-community bridge._
- **Why does `execute_write_dual()` connect `Dual-Write Database Logic` to `Core Business Services`, `Employee Management Logic`, `Database Session Management`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `execute_read_dual()` connect `Read-Only Analytics Queries` to `Core Business Services`, `Employee Management Logic`, `Database Session Management`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `setupEventListeners()` (e.g. with `abrirModalFilasSemCobrador()` and `abrirModalSubstitutoDireto()`) actually correct?**
  _`setupEventListeners()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `api`, `graphify`, `Workflow: graphify` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._