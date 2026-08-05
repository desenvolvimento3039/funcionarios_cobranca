// app.js - Lógica principal e orquestração da aplicação

const state = {
    todosRegistros: [],
    registrosFiltrados: [],
    listaPAs: [],
    timesUnicos: [],
    pasUnicos: [],
    filasUnicas: [],
    filasSemCobrador: [],
    selectedIds: new Set(),
    currentPage: 1,
    itemsPerPage: 25,
    totalServerItems: 0,
    totalServerPages: 1,
    sortColumn: 'id',
    sortDirection: 'desc',
    idParaDeletar: null
};

// ─── Inicialização ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    carregarPAs();
    carregarCobranca();
    carregarAnalytics();
});

async function carregarPAs() {
    try {
        state.listaPAs = await api.getPAs();
        
        const selectsPA = ['item-pa', 'troca-select-pa', 'bulk-pa'];
        selectsPA.forEach(id => {
            const sel = document.getElementById(id);
            if (sel) {
                const firstOption = sel.options[0] ? sel.options[0].outerHTML : '<option value="">Selecione o PA...</option>';
                sel.innerHTML = firstOption;
                state.listaPAs.forEach(pa => {
                    const opt = document.createElement('option');
                    opt.value = pa.num_pa;
                    opt.textContent = `PA ${pa.num_pa} - ${pa.nome_pa || ''}`;
                    sel.appendChild(opt);
                });
            }
        });

        // Renderiza as checkboxes do seletor Multi-PA
        UI.renderizarMultiPASuggestions(state.listaPAs);
    } catch (e) {
        console.error('Erro ao carregar PAs', e);
    }
}

async function carregarAnalytics() {
    try {
        const data = await api.getStats();
        state.substituicoesAtivasCount = data.substituicoes_ativas || 0;
        UI.renderizarGraficos(data);
    } catch (e) {
        console.error('Erro ao carregar stats', e);
    }
}

async function carregarCobranca() {
    try {
        const termo = document.getElementById('search-input')?.value.trim() || '';
        const timeFiltro = document.getElementById('filter-time')?.value || '';
        const paFiltro = document.getElementById('filter-pa')?.value || '';
        const statusFiltro = document.getElementById('filter-status')?.value || '';
        const subFiltro = document.getElementById('filter-substituicao')?.value || '';

        const params = new URLSearchParams({
            page: state.currentPage,
            per_page: state.itemsPerPage,
            sort_by: state.sortColumn,
            sort_order: state.sortDirection
        });
        if (termo) params.append('search', termo);
        if (timeFiltro) params.append('time_cobranca', timeFiltro);
        if (paFiltro) params.append('pa', paFiltro);
        if (statusFiltro !== '') params.append('status', statusFiltro);
        if (subFiltro) params.append('substituicao', subFiltro);
        
        const data = await api.getCobranca(params);
        if (Array.isArray(data)) {
            state.registrosFiltrados = data;
            state.totalServerItems = data.length;
            state.totalServerPages = 1;
        } else {
            state.registrosFiltrados = data.items || [];
            state.totalServerItems = data.total || 0;
            state.totalServerPages = data.total_pages || 1;
            state.currentPage = data.page || 1;
        }

        const all = await api.getCobrancaAll();
        state.todosRegistros = Array.isArray(all) ? all : (all.items || []);
        state.timesUnicos = [...new Set(state.todosRegistros.map(r => r.times_cobranca).filter(Boolean))];
        state.pasUnicos = [...new Set(state.todosRegistros.map(r => r.num_pa))];
        state.filasUnicas = [...new Set(state.todosRegistros.map(r => r.fila).filter(Boolean))];

        populaFiltrosETrocas();

        // Busca filas sem cobradores
        try {
            state.filasSemCobrador = await api.getFilasSemCobradores();
        } catch (e) {
            console.error('Erro ao buscar filas sem cobrador', e);
            state.filasSemCobrador = [];
        }

        UI.renderizarEstatisticas(
            state.totalServerItems, 
            state.timesUnicos.length, 
            state.pasUnicos.length, 
            state.filasUnicas.length, 
            state.filasSemCobrador.length,
            state.substituicoesAtivasCount || 0
        );

        UI.renderizarTabela(
            state.registrosFiltrados, 
            state.totalServerItems, 
            state.currentPage, 
            state.totalServerPages, 
            state.itemsPerPage, 
            (state.currentPage - 1) * state.itemsPerPage + 1, 
            Math.min(state.currentPage * state.itemsPerPage, state.totalServerItems), 
            state.listaPAs,
            state.selectedIds
        );
    } catch (e) {
        console.error('Erro ao carregar cobrança', e);
        UI.showToast('Erro ao carregar dados da tabela', 'error');
    }
}

function populaFiltrosETrocas() {
    // Popula select de filtros
    const selTime = document.getElementById('filter-time');
    if (selTime && selTime.options.length <= 1) {
        state.timesUnicos.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            selTime.appendChild(opt);
        });
    }

    const selPaFilter = document.getElementById('filter-pa');
    if (selPaFilter && selPaFilter.options.length <= 1) {
        state.pasUnicos.sort((a,b)=>a-b).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = `PA ${p}`;
            selPaFilter.appendChild(opt);
        });
    }

    // Popula selects do Modal de Troca em Massa
    const trocaTime = document.getElementById('troca-select-time');
    if (trocaTime) {
        trocaTime.innerHTML = '<option value="">Selecione o Time...</option>';
        state.timesUnicos.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            trocaTime.appendChild(opt);
        });
    }

    const trocaOrig = document.getElementById('troca-select-origem');
    if (trocaOrig) {
        trocaOrig.innerHTML = '<option value="">Selecione o Cobrador de Origem...</option>';
        const cobradoresAgrupados = new Map();
        
        state.todosRegistros.forEach(r => {
            if (r.status === 1 && r.cobrador) {
                const key = `${r.cobrador.trim().toLowerCase()}_${r.matricula}`;
                if (!cobradoresAgrupados.has(key)) {
                    cobradoresAgrupados.set(key, {
                        id: r.id,
                        cobrador: r.cobrador,
                        matricula: r.matricula,
                        count: 1,
                        pas: new Set(r.num_pa !== undefined && r.num_pa !== null ? [r.num_pa] : [])
                    });
                } else {
                    const item = cobradoresAgrupados.get(key);
                    item.count++;
                    if (r.num_pa !== undefined && r.num_pa !== null) item.pas.add(r.num_pa);
                }
            }
        });

        // Ordena por nome do cobrador
        const sortedCobradores = Array.from(cobradoresAgrupados.values()).sort((a, b) => a.cobrador.localeCompare(b.cobrador));

        sortedCobradores.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            const paList = Array.from(c.pas).sort((a, b) => a - b).join(', ');
            opt.textContent = `${c.cobrador} (Mat: ${c.matricula}) — ${c.count} registro(s)${paList ? ` [PAs: ${paList}]` : ''}`;
            trocaOrig.appendChild(opt);
        });
    }

    populaSelectSubstitutos();
}

function populaSelectSubstitutos() {
    const sel = document.getElementById('item-substituto-de');
    if (!sel) return;
    sel.innerHTML = '<option value="">Selecione o cobrador original...</option>';
    const cobradoresAgrupados = new Map();
    state.todosRegistros.forEach(r => {
        if (r.status === 1 && r.cobrador) {
            const key = `${r.cobrador.trim().toLowerCase()}_${r.matricula}`;
            if (!cobradoresAgrupados.has(key)) {
                cobradoresAgrupados.set(key, {
                    id: r.id,
                    cobrador: r.cobrador,
                    matricula: r.matricula,
                    pas: new Set(r.num_pa !== undefined && r.num_pa !== null ? [r.num_pa] : [])
                });
            } else {
                const item = cobradoresAgrupados.get(key);
                if (r.num_pa !== undefined && r.num_pa !== null) item.pas.add(r.num_pa);
            }
        }
    });

    const sorted = Array.from(cobradoresAgrupados.values()).sort((a, b) => a.cobrador.localeCompare(b.cobrador));
    sorted.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        const paList = Array.from(c.pas).sort((a, b) => a - b).join(', ');
        opt.textContent = `${c.cobrador} (Mat: ${c.matricula})${paList ? ` — PAs: ${paList}` : ''}`;
        sel.appendChild(opt);
    });
}

function atualizarContadorMultiPA() {
    const checkedCount = document.querySelectorAll('.item-pa-checkbox:checked').length;
    const el = document.getElementById('multi-pa-count') || document.querySelector('.multi-pa-count-label');
    if (el) {
        el.textContent = `${checkedCount} selecionado(s)`;
    }
}

function setupEventListeners() {
    // Abrir/Fechar Modal de Tutorial (Como Usar)
    document.getElementById('btn-tutorial')?.addEventListener('click', () => {
        const modal = document.getElementById('tutorial-modal');
        if (modal) modal.style.display = 'block';
    });
    document.getElementById('close-tutorial-modal')?.addEventListener('click', () => {
        const modal = document.getElementById('tutorial-modal');
        if (modal) modal.style.display = 'none';
    });
    document.getElementById('btn-close-tutorial')?.addEventListener('click', () => {
        const modal = document.getElementById('tutorial-modal');
        if (modal) modal.style.display = 'none';
    });

    // Alternar exibição do Painel Gráfico / Analytics
    document.getElementById('btn-toggle-analytics')?.addEventListener('click', () => {
        const grid = document.getElementById('charts-grid-content');
        const btn = document.getElementById('btn-toggle-analytics');
        if (!grid || !btn) return;

        if (grid.style.display === 'none') {
            grid.style.display = 'grid';
            btn.innerHTML = '<i class="fa-solid fa-chevron-up"></i> Ocultar Gráficos';
        } else {
            grid.style.display = 'none';
            btn.innerHTML = '<i class="fa-solid fa-chevron-down"></i> Exibir Gráficos';
        }
    });

    // Autocomplete dinâmico de Funcionário (Nome, Matrícula, Time e PA) buscando da tabela fun_funcionario
    const setupFuncAutocomplete = (inputId, suggestionsId, targetCobId, targetMatId, targetTimeId = null) => {
        const inputEl = document.getElementById(inputId);
        const suggEl = document.getElementById(suggestionsId);
        if (!inputEl || !suggEl) return;

        let timer = null;
        inputEl.addEventListener('input', (e) => {
            clearTimeout(timer);
            const val = e.target.value.trim();
            if (val.length < 1) {
                suggEl.style.display = 'none';
                suggEl.innerHTML = '';
                return;
            }

            timer = setTimeout(async () => {
                try {
                    const res = await api.getFuncionariosBusca(val);
                    if (!res || res.length === 0) {
                        suggEl.style.display = 'none';
                        suggEl.innerHTML = '';
                        return;
                    }

                    suggEl.innerHTML = '';
                    res.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'autocomplete-item';
                        
                        let badges = [];
                        if (item.times_cobranca) {
                            badges.push(`<span class="mat-tag" style="background:#e0f2fe; color:#0369a1;">${UI.escapeHtml(item.times_cobranca)}</span>`);
                        }
                        if (item.num_pa !== null && item.num_pa !== undefined) {
                            badges.push(`<span class="mat-tag" style="background:#fef3c7; color:#b45309;">PA ${item.num_pa}</span>`);
                        }
                        badges.push(`<span class="mat-tag">Mat: ${item.matricula}</span>`);

                        div.innerHTML = `
                            <span style="font-weight: 500;">${UI.escapeHtml(item.cobrador || '')}</span>
                            <div style="display:flex; gap:6px; align-items:center;">
                                ${badges.join('')}
                            </div>
                        `;
                        div.addEventListener('click', () => {
                            const inputCob = document.getElementById(targetCobId);
                            const inputMat = document.getElementById(targetMatId);
                            if (inputCob) inputCob.value = item.cobrador || '';
                            if (inputMat) inputMat.value = item.matricula || '';

                            // Preenche o Time de Cobrança se disponível
                            if (targetTimeId && item.times_cobranca) {
                                const inputTime = document.getElementById(targetTimeId);
                                if (inputTime && !inputTime.value.trim()) {
                                    inputTime.value = item.times_cobranca;
                                }
                            }

                            // Marca o PA correspondente se houver no cadastro de novo cobrador
                            if (targetTimeId === 'item-time' && item.num_pa !== null && item.num_pa !== undefined) {
                                const cb = document.querySelector(`.item-pa-checkbox[value="${item.num_pa}"]`);
                                if (cb && !cb.checked) {
                                    cb.checked = true;
                                    atualizarContadorMultiPA();
                                }
                            }

                            suggEl.style.display = 'none';
                            suggEl.innerHTML = '';
                        });
                        suggEl.appendChild(div);
                    });
                    suggEl.style.display = 'block';
                } catch (err) {
                    console.error("Erro no autocomplete:", err);
                }
            }, 250);
        });

        document.addEventListener('click', (ev) => {
            if (!inputEl.contains(ev.target) && !suggEl.contains(ev.target)) {
                suggEl.style.display = 'none';
            }
        });
    };

    // Autocomplete no Modal de Novo Cobrador (traz também Time e PA)
    setupFuncAutocomplete('item-cobrador', 'cobrador-suggestions', 'item-cobrador', 'item-matricula', 'item-time');
    setupFuncAutocomplete('item-matricula', 'matricula-suggestions', 'item-cobrador', 'item-matricula', 'item-time');

    // Autocomplete no Modal de Troca em Massa (traz também Time)
    setupFuncAutocomplete('troca-novo-cobrador', 'troca-cobrador-suggestions', 'troca-novo-cobrador', 'troca-nova-matricula');
    setupFuncAutocomplete('troca-nova-matricula', 'troca-matricula-suggestions', 'troca-novo-cobrador', 'troca-nova-matricula');

    // Checkbox de Substituto Temporário (Abre/Fecha campos de substituto)
    document.getElementById('item-is-substituto')?.addEventListener('change', (e) => {
        const fields = document.getElementById('substituto-fields');
        if (fields) {
            fields.style.display = e.target.checked ? 'block' : 'none';
        }
    });

    // Busca rápida de PAs no seletor Multi-PA
    document.getElementById('multi-pa-search-input')?.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.multi-pa-item').forEach(item => {
            const text = item.getAttribute('data-pa-text') || '';
            if (!term || text.includes(term)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });

    // Checkbox Selecionar Todos os PAs visíveis no cadastro
    document.getElementById('item-pa-select-all')?.addEventListener('change', (e) => {
        const isChecked = e.target.checked;
        document.querySelectorAll('.multi-pa-item').forEach(item => {
            if (item.style.display !== 'none') {
                const cb = item.querySelector('.item-pa-checkbox');
                if (cb) cb.checked = isChecked;
            }
        });
        atualizarContadorMultiPA();
    });

    document.getElementById('item-pas-grid')?.addEventListener('change', (e) => {
        if (e.target.classList.contains('item-pa-checkbox')) {
            atualizarContadorMultiPA();
        }
    });

    // Delegação de eventos na Tabela (Botões de Ação)
    document.getElementById('cobranca-tbody')?.addEventListener('click', (e) => {
        const btn = e.target.closest('button[data-action]');
        if (btn) {
            const action = btn.dataset.action;
            const id = parseInt(btn.dataset.id);

            if (action === 'toggle-status') {
                const targetStatus = parseInt(btn.dataset.targetStatus);
                alternarStatus(id, targetStatus);
            } else if (action === 'edit') {
                editarItem(id);
            } else if (action === 'delete') {
                confirmarExclusao(id);
            } else if (action === 'substituir-linha') {
                abrirModalSubstitutoDireto({
                    id: id,
                    cobrador: btn.dataset.cobrador,
                    matricula: btn.dataset.matricula
                });
            } else if (action === 'cancelar-substituicao') {
                const subId = parseInt(btn.dataset.subId);
                cancelarSubstituicao(subId);
            }
            return;
        }

        // Checkbox individual da linha
        if (e.target.classList.contains('row-checkbox')) {
            const id = parseInt(e.target.dataset.id);
            if (e.target.checked) {
                state.selectedIds.add(id);
            } else {
                state.selectedIds.delete(id);
            }
            UI.atualizarBarraLote(state.selectedIds.size);
        }
    });

    // Checkbox Selecionar Todos na Tabela
    document.getElementById('select-all-rows')?.addEventListener('change', (e) => {
        const isChecked = e.target.checked;
        state.registrosFiltrados.forEach(r => {
            if (isChecked) {
                state.selectedIds.add(r.id);
            } else {
                state.selectedIds.delete(r.id);
            }
        });
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = isChecked);
        UI.atualizarBarraLote(state.selectedIds.size);
    });

    // Ações da Barra Flutuante de Seleção em Lote (Bulk Actions)
    document.getElementById('btn-bulk-clear')?.addEventListener('click', () => {
        state.selectedIds.clear();
        const chkAll = document.getElementById('select-all-rows');
        if (chkAll) chkAll.checked = false;
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
        UI.atualizarBarraLote(0);
    });

    document.getElementById('btn-bulk-edit')?.addEventListener('click', () => abrirModalBulkForm());
    document.getElementById('close-bulk-modal')?.addEventListener('click', fecharModalBulkForm);
    document.getElementById('btn-cancel-bulk')?.addEventListener('click', fecharModalBulkForm);
    document.getElementById('bulk-form')?.addEventListener('submit', executarBulkUpdate);

    document.getElementById('btn-bulk-inativar')?.addEventListener('click', async () => {
        if (state.selectedIds.size === 0) return;
        if (confirm(`Deseja inativar os ${state.selectedIds.size} registros selecionados?`)) {
            try {
                await api.bulkUpdate({
                    ids: Array.from(state.selectedIds),
                    novo_status: 0
                });
                UI.showToast(`${state.selectedIds.size} registros inativados!`, 'success');
                state.selectedIds.clear();
                carregarCobranca();
                carregarAnalytics();
            } catch (err) {
                UI.showToast(err.message, 'error');
            }
        }
    });

    // Helper de debounce para otimização de busca por texto
    const debounce = (fn, delay = 300) => {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    };

    // Filtros e paginação
    document.getElementById('search-input')?.addEventListener('input', debounce(() => { state.currentPage = 1; carregarCobranca(); }, 300));
    document.getElementById('filter-time')?.addEventListener('change', () => { state.currentPage = 1; carregarCobranca(); });
    document.getElementById('filter-pa')?.addEventListener('change', () => { state.currentPage = 1; carregarCobranca(); });
    document.getElementById('filter-status')?.addEventListener('change', () => { state.currentPage = 1; carregarCobranca(); });
    document.getElementById('filter-substituicao')?.addEventListener('change', () => { state.currentPage = 1; carregarCobranca(); });
    
    document.getElementById('per-page-select')?.addEventListener('change', (e) => { state.itemsPerPage = parseInt(e.target.value); state.currentPage = 1; carregarCobranca(); });
    document.getElementById('btn-prev-page')?.addEventListener('click', () => { if (state.currentPage > 1) { state.currentPage--; carregarCobranca(); } });
    document.getElementById('btn-next-page')?.addEventListener('click', () => { if (state.currentPage < state.totalServerPages) { state.currentPage++; carregarCobranca(); } });
    
    // Cadastro de cobrador individual / multi-pa
    document.getElementById('btn-add-item')?.addEventListener('click', () => abrirModalItem());
    document.getElementById('close-modal')?.addEventListener('click', fecharModalItem);
    document.getElementById('btn-cancel-modal')?.addEventListener('click', fecharModalItem);
    document.getElementById('item-form')?.addEventListener('submit', salvarItem);

    // MODAL 📅 ESCALA DE SUBSTITUIÇÕES
    document.getElementById('btn-escala-substituicoes')?.addEventListener('click', abrirModalEscalaSubstituicoes);
    document.getElementById('card-substituicoes-ativas')?.addEventListener('click', abrirModalEscalaSubstituicoes);
    document.getElementById('close-escala-modal')?.addEventListener('click', fecharModalEscalaSubstituicoes);
    document.getElementById('btn-close-escala')?.addEventListener('click', fecharModalEscalaSubstituicoes);
    document.getElementById('btn-escala-nova-substituicao')?.addEventListener('click', () => {
        fecharModalEscalaSubstituicoes();
        abrirModalSubstitutoDireto();
    });

    document.querySelectorAll('.escala-filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.escala-filter-btn').forEach(b => b.classList.remove('active'));
            const btnTarget = e.currentTarget || e.target;
            btnTarget.classList.add('active');
            const st = btnTarget.dataset.escalaStatus;
            state.escalaFiltroAtual = st;
            UI.renderizarEscalaSubstituicoes(state.escalaDataCache || [], st);
        });
    });

    document.getElementById('escala-tbody')?.addEventListener('click', async (e) => {
        const btn = e.target.closest('button[data-action="cancelar-substituicao-escala"]');
        if (btn) {
            const subId = parseInt(btn.dataset.subId);
            if (confirm('Deseja realmente cancelar esta substituição?')) {
                try {
                    await api.cancelarSubstituicao(subId);
                    UI.showToast('Substituição cancelada com sucesso!', 'success');
                    state.escalaDataCache = await api.getSubstituicoesEscala();
                    UI.renderizarEscalaSubstituicoes(state.escalaDataCache, state.escalaFiltroAtual || 'TODAS');
                    carregarCobranca();
                    carregarAnalytics();
                } catch (err) {
                    UI.showToast(err.message, 'error');
                }
            }
        }
    });

    // MODAL ⚡ TROCA EM MASSA
    document.getElementById('btn-troca-massa')?.addEventListener('click', abrirModalTrocaMassa);
    document.getElementById('close-troca-massa-modal')?.addEventListener('click', fecharModalTrocaMassa);
    document.getElementById('btn-cancel-troca-massa')?.addEventListener('click', fecharModalTrocaMassa);
    document.getElementById('troca-massa-form')?.addEventListener('submit', executarTrocaMassa);

    // Abas do Modal Troca em Massa
    document.querySelectorAll('#troca-massa-modal .tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('#troca-massa-modal .tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('#troca-massa-modal .tab-content').forEach(c => c.style.display = 'none');
            
            e.target.classList.add('active');
            const targetTab = e.target.dataset.tab;
            const elTab = document.getElementById(targetTab);
            if (elTab) elTab.style.display = 'block';
        });
    });

    // MODAL 📜 HISTÓRICO DE AUDITORIA
    document.getElementById('btn-historico-auditoria')?.addEventListener('click', abrirModalAuditoria);
    document.getElementById('close-auditoria-modal')?.addEventListener('click', fecharModalAuditoria);
    document.getElementById('btn-close-auditoria')?.addEventListener('click', fecharModalAuditoria);

    // Modal confirmação de exclusão
    document.getElementById('close-confirm-modal')?.addEventListener('click', fecharConfirmModal);
    document.getElementById('btn-cancel-confirm')?.addEventListener('click', fecharConfirmModal);
    document.getElementById('btn-action-confirm')?.addEventListener('click', executarExclusaoConfirmada);

    // Sincronização e Excel / CSV
    document.getElementById('btn-sync')?.addEventListener('click', sincronizarBancos);
    document.getElementById('btn-export-csv')?.addEventListener('click', () => api.exportarCSV());

    // MODAL 📊 MODELO E IMPORTAÇÃO EXCEL
    document.getElementById('btn-upload-excel')?.addEventListener('click', abrirModalExcel);
    document.getElementById('close-excel-modal')?.addEventListener('click', fecharModalExcel);
    document.getElementById('btn-cancel-excel')?.addEventListener('click', fecharModalExcel);
    document.getElementById('btn-download-modelo-excel')?.addEventListener('click', () => api.downloadModeloExcel());
    document.getElementById('btn-submit-upload-excel')?.addEventListener('click', executarUploadExcelModal);
    
    // Modal Substituto Direto (Com Abas e Busca por Autocomplete)
    document.getElementById('btn-add-substituto')?.addEventListener('click', abrirModalSubstitutoDireto);
    document.getElementById('close-sub-dir-modal')?.addEventListener('click', fecharModalSubstitutoDireto);
    document.getElementById('btn-cancel-sub-dir')?.addEventListener('click', fecharModalSubstitutoDireto);
    document.getElementById('btn-cancel-sub-massa')?.addEventListener('click', fecharModalSubstitutoDireto);
    document.getElementById('sub-dir-form')?.addEventListener('submit', salvarSubstitutoDireto);
    document.getElementById('sub-massa-form')?.addEventListener('submit', salvarSubstituicaoMassa);

    // Abas do Modal de Substituição (Individual vs Massa)
    document.querySelectorAll('#substituto-direto-modal .tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('#substituto-direto-modal .tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('#substituto-direto-modal .tab-content').forEach(c => c.style.display = 'none');
            
            const btnTarget = e.currentTarget || e.target;
            btnTarget.classList.add('active');
            const targetTab = btnTarget.dataset.tab;
            const elTab = document.getElementById(targetTab);
            if (elTab) elTab.style.display = 'block';
        });
    });

    // Sub-abas do Modo de Substituição em Massa (Time vs PA vs Cobrador)
    document.querySelectorAll('.sub-massa-tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.sub-massa-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.sub-massa-mode-content').forEach(c => c.style.display = 'none');

            e.target.classList.add('active');
            const mode = e.target.dataset.massaMode;
            const elMode = document.getElementById(`sub-massa-mode-${mode}`);
            if (elMode) elMode.style.display = 'block';
        });
    });

    // Autocompletes do Modal de Substituição
    setupSubOriginalAutocomplete();
    setupSubSubstitutoAutocomplete('sub-dir-sub-search', 'sub-dir-sub-id', 'sub-dir-sub-suggestions', 'sub-dir-sub-selected-info');
    setupSubSubstitutoAutocomplete('sub-massa-sub-search', 'sub-massa-sub-id', 'sub-massa-sub-suggestions', 'sub-massa-sub-selected-info');

    // Card de Filas Sem Cobradores
    document.getElementById('card-filas-sem-cobrador')?.addEventListener('click', abrirModalFilasSemCobrador);
    document.getElementById('close-filas-sem-cob-modal')?.addEventListener('click', fecharModalFilasSemCobrador);
    document.getElementById('btn-close-filas-sem-cob')?.addEventListener('click', fecharModalFilasSemCobrador);
}

function atualizarContadorMultiPA() {
    const selected = document.querySelectorAll('.item-pa-checkbox:checked');
    const spanCount = document.getElementById('multi-pa-count');
    if (spanCount) spanCount.textContent = `${selected.length} selecionado(s)`;
}

// ─── CADASTRO / EDIÇÃO DE COBRADOR (NOVO COBRADOR MULTI-PA) ──────────────────
function abrirModalItem(item = null) {
    document.getElementById('item-form').reset();
    document.getElementById('substituto-fields').style.display = 'none';
    const chkSub = document.getElementById('item-is-substituto');
    if (chkSub) chkSub.checked = false;

    const searchPA = document.getElementById('multi-pa-search-input');
    if (searchPA) searchPA.value = '';

    const chkAll = document.getElementById('item-pa-select-all');
    if (chkAll) chkAll.checked = false;
    document.querySelectorAll('.item-pa-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('.multi-pa-item').forEach(item => item.style.display = 'flex');
    atualizarContadorMultiPA();
    populaSelectSubstitutos();
    
    const singleWrapper = document.getElementById('single-pa-wrapper');
    const multiWrapper = document.getElementById('multi-pa-wrapper');

    if (item) {
        document.getElementById('modal-title').textContent = 'Editar Cobrador';
        document.getElementById('item-id').value = item.id;
        document.getElementById('item-time').value = item.times_cobranca || '';
        document.getElementById('item-pa').value = item.num_pa || '';
        document.getElementById('item-matricula').value = item.matricula || '';
        document.getElementById('item-cobrador').value = item.cobrador || '';
        document.getElementById('item-fila').value = item.fila || '';
        document.getElementById('item-fone').value = item.telefone || '';
        document.getElementById('item-status').value = (item.status === 0) ? '0' : '1';
        document.getElementById('item-is-substituto').disabled = true;

        if (singleWrapper) singleWrapper.style.display = 'block';
        if (multiWrapper) multiWrapper.style.display = 'none';
    } else {
        document.getElementById('modal-title').textContent = 'Novo Cobrador';
        document.getElementById('item-id').value = '';
        document.getElementById('item-is-substituto').disabled = false;

        if (singleWrapper) singleWrapper.style.display = 'none';
        if (multiWrapper) multiWrapper.style.display = 'block';
    }
    document.getElementById('item-modal').style.display = 'block';
}

function fecharModalItem() {
    document.getElementById('item-modal').style.display = 'none';
}

async function salvarItem(e) {
    e.preventDefault();
    const id = document.getElementById('item-id').value;
    const isSubstituto = document.getElementById('item-is-substituto')?.checked;

    let num_pa = 0;
    let num_pas = [];

    if (id) {
        // Edição individual
        num_pa = parseInt(document.getElementById('item-pa').value) || 0;
    } else {
        // Criação de Novo Cobrador com Multi-PA
        const checkedPAs = Array.from(document.querySelectorAll('.item-pa-checkbox:checked')).map(cb => parseInt(cb.value));
        if (checkedPAs.length === 0) {
            UI.showToast('Selecione pelo menos um PA para o novo cobrador.', 'error');
            return;
        }
        num_pas = checkedPAs;
        num_pa = checkedPAs[0];
    }
    
    const payload = {
        times_cobranca: document.getElementById('item-time').value.trim(),
        num_pa,
        num_pas,
        matricula: parseInt(document.getElementById('item-matricula').value),
        cobrador: document.getElementById('item-cobrador').value.trim(),
        fila: document.getElementById('item-fila').value.trim(),
        telefone: document.getElementById('item-fone').value.trim(),
        status: parseInt(document.getElementById('item-status').value)
    };
    
    if (isSubstituto && !id) {
        payload.is_substituto = true;
        payload.substituto_de_id = parseInt(document.getElementById('item-substituto-de').value);
        payload.data_inicio_substituicao = document.getElementById('item-data-inicio').value;
        payload.data_fim_substituicao = document.getElementById('item-data-fim').value;
        
        if (!payload.substituto_de_id || !payload.data_inicio_substituicao || !payload.data_fim_substituicao) {
            UI.showToast('Preencha os dados do substituto.', 'error');
            return;
        }
    }

    try {
        await api.saveCobranca(id, payload);
        const msg = id ? 'Cobrador atualizado!' : `${num_pas.length} registro(s) de cobrador criado(s) com sucesso!`;
        UI.showToast(msg, 'success');
        fecharModalItem();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── LÓGICA DO MODAL ⚡ TROCA EM MASSA ───────────────────────────────────────
function abrirModalTrocaMassa() {
    populaFiltrosETrocas();
    document.getElementById('troca-massa-form').reset();
    document.getElementById('troca-massa-modal').style.display = 'block';
}

function fecharModalTrocaMassa() {
    document.getElementById('troca-massa-modal').style.display = 'none';
}

async function executarTrocaMassa(e) {
    e.preventDefault();
    const activeTab = document.querySelector('#troca-massa-modal .tab-btn.active')?.dataset.tab;

    let modo = 'time';
    let time = null;
    let num_pa = null;
    let cobrador_origem_id = null;

    if (activeTab === 'tab-time') {
        modo = 'time';
        time = document.getElementById('troca-select-time').value;
        if (!time) return UI.showToast('Selecione um Time de Cobrança.', 'error');
    } else if (activeTab === 'tab-pa') {
        modo = 'pa';
        num_pa = parseInt(document.getElementById('troca-select-pa').value);
        if (!num_pa) return UI.showToast('Selecione um PA.', 'error');
    } else if (activeTab === 'tab-cobrador') {
        modo = 'cobrador';
        cobrador_origem_id = parseInt(document.getElementById('troca-select-origem').value);
        if (!cobrador_origem_id) return UI.showToast('Selecione o Cobrador de Origem.', 'error');
    }

    const payload = {
        modo,
        time,
        num_pa,
        cobrador_origem_id,
        novo_cobrador: document.getElementById('troca-novo-cobrador').value.trim(),
        nova_matricula: parseInt(document.getElementById('troca-nova-matricula').value),
        inativar_origem: document.getElementById('troca-inativar-origem').checked
    };

    try {
        const res = await api.trocaMassa(payload);
        UI.showToast(res.mensagem || 'Troca em massa realizada!', 'success');
        fecharModalTrocaMassa();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── LÓGICA DO MODAL BULK FORM ──────────────────────────────────────────────
function abrirModalBulkForm() {
    if (state.selectedIds.size === 0) return UI.showToast('Selecione pelo menos um item.', 'error');
    document.getElementById('bulk-form').reset();
    document.getElementById('bulk-modal').style.display = 'block';
}

function fecharModalBulkForm() {
    document.getElementById('bulk-modal').style.display = 'none';
}

async function executarBulkUpdate(e) {
    e.preventDefault();
    const payload = {
        ids: Array.from(state.selectedIds),
        novo_cobrador: document.getElementById('bulk-cobrador').value.trim() || null,
        nova_matricula: document.getElementById('bulk-matricula').value ? parseInt(document.getElementById('bulk-matricula').value) : null,
        novo_time: document.getElementById('bulk-time').value.trim() || null,
        novo_pa: document.getElementById('bulk-pa').value ? parseInt(document.getElementById('bulk-pa').value) : null
    };

    try {
        const res = await api.bulkUpdate(payload);
        UI.showToast(res.mensagem || 'Atualização em lote concluída!', 'success');
        fecharModalBulkForm();
        state.selectedIds.clear();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── LÓGICA DO MODAL 📜 HISTÓRICO DE AUDITORIA ──────────────────────────────
async function abrirModalAuditoria() {
    try {
        const data = await api.getHistoricoAuditoria();
        UI.renderizarAuditoria(data);
        document.getElementById('auditoria-modal').style.display = 'block';
    } catch (err) {
        UI.showToast('Erro ao carregar Histórico de Auditoria', 'error');
    }
}

function fecharModalAuditoria() {
    document.getElementById('auditoria-modal').style.display = 'none';
}

// ─── MODAL SUBSTITUTO DIRETO ────────────────────────────────────────────────
// ─── MODAL SUBSTITUIÇÃO TEMPORÁRIA (INDIVIDUAL E EM MASSA) ─────────────────
function setupSubOriginalAutocomplete() {
    const inputEl = document.getElementById('sub-dir-orig-search');
    const hiddenIdEl = document.getElementById('sub-dir-orig-id');
    const suggEl = document.getElementById('sub-dir-orig-suggestions');
    const infoEl = document.getElementById('sub-dir-orig-selected-info');
    if (!inputEl || !suggEl) return;

    let timer = null;
    inputEl.addEventListener('input', (e) => {
        clearTimeout(timer);
        const val = e.target.value.trim();
        if (hiddenIdEl) hiddenIdEl.value = '';
        if (infoEl) infoEl.style.display = 'none';

        if (val.length < 1) {
            suggEl.style.display = 'none';
            suggEl.innerHTML = '';
            return;
        }

        timer = setTimeout(async () => {
            try {
                const res = await api.getFuncionariosBusca(val);
                if (!res || res.length === 0) {
                    suggEl.style.display = 'none';
                    suggEl.innerHTML = '';
                    return;
                }

                suggEl.innerHTML = '';
                res.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';

                    let badges = [];
                    if (item.times_cobranca) {
                        badges.push(`<span class="mat-tag" style="background:#e0f2fe; color:#0369a1;">${UI.escapeHtml(item.times_cobranca)}</span>`);
                    }
                    if (item.num_pa !== null && item.num_pa !== undefined) {
                        badges.push(`<span class="mat-tag" style="background:#fef3c7; color:#b45309;">PA ${item.num_pa}</span>`);
                    }
                    if (item.fila) {
                        badges.push(`<span class="mat-tag" style="background:#f0fdf4; color:#15803d; font-weight:600;">Fila: ${UI.escapeHtml(item.fila)}</span>`);
                    }
                    badges.push(`<span class="mat-tag">Mat: ${item.matricula}</span>`);

                    div.innerHTML = `
                        <div style="font-weight: 600; color:#0f172a;">${UI.escapeHtml(item.cobrador || '')}</div>
                        <div style="display:flex; gap:4px; align-items:center; margin-top:4px; flex-wrap:wrap;">
                            ${badges.join('')}
                        </div>
                    `;

                    div.addEventListener('click', () => {
                        inputEl.value = item.cobrador || '';
                        const chosenId = item.cobranca_id || item.id;
                        if (hiddenIdEl) hiddenIdEl.value = chosenId;
                        if (infoEl) {
                            infoEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> Selecionado: <strong>${UI.escapeHtml(item.cobrador)}</strong> (Mat: ${item.matricula}) ${item.times_cobranca ? `— Time: ${UI.escapeHtml(item.times_cobranca)}` : ''} | PA ${item.num_pa} ${item.fila ? `| <strong>Fila: ${UI.escapeHtml(item.fila)}</strong>` : ''}`;
                            infoEl.style.display = 'block';
                        }
                        suggEl.style.display = 'none';
                    });
                    suggEl.appendChild(div);
                });
                suggEl.style.display = 'block';
            } catch (err) {
                console.error("Erro no autocomplete:", err);
            }
        }, 200);
    });

    document.addEventListener('click', (ev) => {
        if (!inputEl.contains(ev.target) && !suggEl.contains(ev.target)) {
            suggEl.style.display = 'none';
        }
    });
}

function setupSubSubstitutoAutocomplete(inputId, hiddenId, suggestionsId, infoId) {
    const inputEl = document.getElementById(inputId);
    const hiddenIdEl = document.getElementById(hiddenId);
    const suggEl = document.getElementById(suggestionsId);
    const infoEl = document.getElementById(infoId);
    if (!inputEl || !suggEl) return;

    let timer = null;
    inputEl.addEventListener('input', (e) => {
        clearTimeout(timer);
        const val = e.target.value.trim();
        if (hiddenIdEl) hiddenIdEl.value = '';
        if (infoEl) infoEl.style.display = 'none';

        if (val.length < 1) {
            suggEl.style.display = 'none';
            suggEl.innerHTML = '';
            return;
        }

        timer = setTimeout(async () => {
            try {
                const res = await api.getFuncionariosBusca(val);
                if (!res || res.length === 0) {
                    suggEl.style.display = 'none';
                    suggEl.innerHTML = '';
                    return;
                }

                suggEl.innerHTML = '';
                res.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';

                    let badges = [];
                    if (item.times_cobranca) {
                        badges.push(`<span class="mat-tag" style="background:#e0f2fe; color:#0369a1;">${UI.escapeHtml(item.times_cobranca)}</span>`);
                    }
                    if (item.num_pa !== null && item.num_pa !== undefined) {
                        badges.push(`<span class="mat-tag" style="background:#fef3c7; color:#b45309;">PA ${item.num_pa}</span>`);
                    }
                    badges.push(`<span class="mat-tag">Mat: ${item.matricula}</span>`);

                    div.innerHTML = `
                        <div style="font-weight: 600; color:#0f172a;">${UI.escapeHtml(item.cobrador || '')}</div>
                        <div style="display:flex; gap:4px; align-items:center; margin-top:4px; flex-wrap:wrap;">
                            ${badges.join('')}
                        </div>
                    `;

                    div.addEventListener('click', () => {
                        inputEl.value = item.cobrador || '';
                        const chosenId = item.cobranca_id || item.id;
                        if (hiddenIdEl) hiddenIdEl.value = chosenId;
                        if (infoEl) {
                            infoEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> Substituto Selecionado: <strong>${UI.escapeHtml(item.cobrador)}</strong> (Mat: ${item.matricula})`;
                            infoEl.style.display = 'block';
                        }
                        suggEl.style.display = 'none';
                    });
                    suggEl.appendChild(div);
                });
                suggEl.style.display = 'block';
            } catch (err) {
                console.error("Erro no autocomplete:", err);
            }
        }, 200);
    });

    document.addEventListener('click', (ev) => {
        if (!inputEl.contains(ev.target) && !suggEl.contains(ev.target)) {
            suggEl.style.display = 'none';
        }
    });
}

function abrirModalSubstitutoDireto(cobradorOrigem = null) {
    document.getElementById('sub-dir-form')?.reset();
    document.getElementById('sub-massa-form')?.reset();

    // Garante que a primeira aba fique ativa ao abrir o modal
    document.querySelectorAll('#substituto-direto-modal .tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('#substituto-direto-modal .tab-content').forEach(c => c.style.display = 'none');
    const firstTabBtn = document.querySelector('#substituto-direto-modal .tab-btn');
    if (firstTabBtn) firstTabBtn.classList.add('active');
    const firstForm = document.getElementById('sub-dir-form');
    if (firstForm) firstForm.style.display = 'block';
    
    ['sub-dir-orig-id', 'sub-dir-sub-id', 'sub-massa-sub-id'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });

    ['sub-dir-orig-selected-info', 'sub-dir-sub-selected-info', 'sub-massa-sub-selected-info'].forEach(id => {
        const el = document.getElementById(id);
        if (el) { el.style.display = 'none'; el.innerHTML = ''; }
    });

    if (cobradorOrigem && cobradorOrigem.id) {
        const inputOrig = document.getElementById('sub-dir-orig-search');
        const hiddenOrig = document.getElementById('sub-dir-orig-id');
        const infoOrig = document.getElementById('sub-dir-orig-selected-info');
        if (inputOrig) inputOrig.value = cobradorOrigem.cobrador || '';
        if (hiddenOrig) hiddenOrig.value = cobradorOrigem.id;
        if (infoOrig) {
            infoOrig.innerHTML = `<i class="fa-solid fa-circle-check"></i> Selecionado: <strong>${UI.escapeHtml(cobradorOrigem.cobrador)}</strong> (Mat: ${cobradorOrigem.matricula}) — <em>O substituto assumirá <strong>TODAS AS FILAS</strong> deste cobrador.</em>`;
            infoOrig.style.display = 'block';
        }
    }

    // Popula selects da aba de Substituição em Massa
    const selTime = document.getElementById('sub-massa-select-time');
    if (selTime) {
        selTime.innerHTML = '<option value="">Selecione o Time...</option>';
        state.timesUnicos.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            selTime.appendChild(opt);
        });
    }

    const selPa = document.getElementById('sub-massa-select-pa');
    if (selPa) {
        selPa.innerHTML = '<option value="">Selecione o PA...</option>';
        state.pasUnicos.sort((a,b)=>a-b).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = `PA ${p}`;
            selPa.appendChild(opt);
        });
    }

    const selOrig = document.getElementById('sub-massa-select-origem');
    if (selOrig) {
        selOrig.innerHTML = '<option value="">Selecione o Cobrador Original...</option>';
        const cobradoresAgrupados = new Map();
        state.todosRegistros.forEach(r => {
            if (r.status === 1 && r.cobrador) {
                const key = `${r.cobrador.trim().toLowerCase()}_${r.matricula}`;
                if (!cobradoresAgrupados.has(key)) {
                    cobradoresAgrupados.set(key, { id: r.id, cobrador: r.cobrador, matricula: r.matricula, pas: new Set(r.num_pa !== undefined ? [r.num_pa] : []) });
                } else {
                    const item = cobradoresAgrupados.get(key);
                    if (r.num_pa !== undefined) item.pas.add(r.num_pa);
                }
            }
        });
        const sorted = Array.from(cobradoresAgrupados.values()).sort((a, b) => a.cobrador.localeCompare(b.cobrador));
        sorted.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            const paList = Array.from(c.pas).sort((a, b) => a - b).join(', ');
            opt.textContent = `${c.cobrador} (Mat: ${c.matricula})${paList ? ` — PAs: ${paList}` : ''}`;
            selOrig.appendChild(opt);
        });
    }
    
    document.getElementById('substituto-direto-modal').style.display = 'block';
}

function fecharModalSubstitutoDireto() {
    document.getElementById('substituto-direto-modal').style.display = 'none';
}

async function salvarSubstitutoDireto(e) {
    e.preventDefault();
    const origId = parseInt(document.getElementById('sub-dir-orig-id').value);
    const subId = parseInt(document.getElementById('sub-dir-sub-id').value);
    const dtIni = document.getElementById('sub-dir-inicio').value;
    const dtFim = document.getElementById('sub-dir-fim').value;

    if (!origId) return UI.showToast('Selecione o cobrador original sendo substituído pela busca.', 'error');
    if (!subId) return UI.showToast('Selecione o cobrador substituto pela busca.', 'error');
    if (origId === subId) return UI.showToast('O substituto não pode ser igual ao funcionário original.', 'error');
    if (!dtIni || !dtFim) return UI.showToast('Preencha as datas de início e fim.', 'error');

    const payload = {
        original_id: origId,
        substituto_id: subId,
        data_inicio: dtIni,
        data_fim: dtFim
    };

    try {
        await api.saveSubstituicaoDireta(payload);
        UI.showToast('Substituição individual agendada com sucesso!', 'success');
        fecharModalSubstitutoDireto();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

async function salvarSubstituicaoMassa(e) {
    e.preventDefault();
    const activeModeBtn = document.querySelector('.sub-massa-tab-btn.active');
    const modo = activeModeBtn ? activeModeBtn.dataset.massaMode : 'time';

    let time = null;
    let num_pa = null;
    let cobrador_origem_id = null;

    if (modo === 'time') {
        time = document.getElementById('sub-massa-select-time').value;
        if (!time) return UI.showToast('Selecione o Time a substituir.', 'error');
    } else if (modo === 'pa') {
        num_pa = parseInt(document.getElementById('sub-massa-select-pa').value);
        if (!num_pa) return UI.showToast('Selecione o PA a substituir.', 'error');
    } else if (modo === 'cobrador') {
        cobrador_origem_id = parseInt(document.getElementById('sub-massa-select-origem').value);
        if (!cobrador_origem_id) return UI.showToast('Selecione o Cobrador Original.', 'error');
    }

    const subId = parseInt(document.getElementById('sub-massa-sub-id').value);
    const dtIni = document.getElementById('sub-massa-inicio').value;
    const dtFim = document.getElementById('sub-massa-fim').value;

    if (!subId) return UI.showToast('Selecione o cobrador substituto que assumirá o grupo.', 'error');
    if (!dtIni || !dtFim) return UI.showToast('Preencha as datas de início e fim da substituição.', 'error');

    const payload = {
        modo,
        time,
        num_pa,
        cobrador_origem_id,
        substituto_id: subId,
        data_inicio: dtIni,
        data_fim: dtFim
    };

    try {
        const res = await api.saveSubstituicaoMassa(payload);
        UI.showToast(res.mensagem || 'Substituição em massa temporária agendada com sucesso!', 'success');
        fecharModalSubstitutoDireto();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── MODAL FILAS SEM COBRADOR ────────────────────────────────────────────────
function abrirModalFilasSemCobrador() {
    UI.renderizarFilasSemCobrador(state.filasSemCobrador, adicionarCobradorFilaCallback);
    document.getElementById('filas-sem-cobrador-modal').style.display = 'block';
}

function fecharModalFilasSemCobrador() {
    document.getElementById('filas-sem-cobrador-modal').style.display = 'none';
}

function adicionarCobradorFilaCallback(nomeFila, numPA = 0) {
    fecharModalFilasSemCobrador();
    abrirModalItem();
    const inputFila = document.getElementById('item-fila');
    if (inputFila) {
        inputFila.value = nomeFila;
        inputFila.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (numPA && parseInt(numPA) > 0) {
        document.querySelectorAll('.item-pa-checkbox').forEach(cb => {
            cb.checked = (parseInt(cb.value) === parseInt(numPA));
        });
        atualizarContadorMultiPA();
    }
}

function abrirModalExcel() {
    const input = document.getElementById('excel-file-input');
    if (input) input.value = '';
    const modal = document.getElementById('excel-modal');
    if (modal) modal.style.display = 'block';
}

function fecharModalExcel() {
    const modal = document.getElementById('excel-modal');
    if (modal) modal.style.display = 'none';
}

async function executarUploadExcelModal() {
    const fileInput = document.getElementById('excel-file-input');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        return UI.showToast('Selecione um arquivo Excel ou CSV para fazer upload.', 'error');
    }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        UI.showToast('Enviando e processando arquivo...', 'info');
        const res = await api.uploadExcel(formData);
        UI.showToast(res.message || 'Arquivo processado com sucesso!', 'success');
        fecharModalExcel();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message || 'Erro ao importar arquivo Excel', 'error');
    }
}

async function cancelarSubstituicao(subId) {
    if (!subId) return;
    if (confirm('Deseja realmente cancelar esta substituição?')) {
        try {
            await api.cancelarSubstituicao(subId);
            UI.showToast('Substituição cancelada com sucesso!', 'success');
            carregarCobranca();
            carregarAnalytics();
        } catch (err) {
            UI.showToast(err.message || 'Erro ao cancelar substituição', 'error');
        }
    }
}

function editarItem(id) {
    const item = state.registrosFiltrados.find(r => r.id === id) || state.todosRegistros.find(r => r.id === id);
    if (item) abrirModalItem(item);
}

async function alternarStatus(id, status) {
    try {
        await api.toggleStatus(id, status);
        UI.showToast('Status alterado!', 'success');
        carregarCobranca();
    } catch (e) {
        UI.showToast('Erro ao alterar status', 'error');
    }
}

function confirmarExclusao(id) {
    state.idParaDeletar = id;
    document.getElementById('confirm-modal').style.display = 'block';
}

function fecharConfirmModal() {
    document.getElementById('confirm-modal').style.display = 'none';
    state.idParaDeletar = null;
}

async function executarExclusaoConfirmada() {
    if (!state.idParaDeletar) return;
    try {
        await api.deleteCobranca(state.idParaDeletar);
        fecharConfirmModal();
        UI.showToast('Excluído com sucesso!', 'success');
        carregarCobranca();
    } catch (e) {
        UI.showToast('Erro ao excluir', 'error');
    }
}

async function sincronizarBancos() {
    try {
        UI.showToast('Sincronizando...', 'info');
        await api.syncDb();
        UI.showToast('Sincronização concluída!', 'success');
        carregarCobranca();
    } catch (e) {
        UI.showToast('Erro na sincronização', 'error');
    }
}

// ─── LÓGICA DO MODAL 📅 ESCALA DE SUBSTITUIÇÕES E FÉRIAS ──────────────────
async function abrirModalEscalaSubstituicoes() {
    try {
        state.escalaDataCache = await api.getSubstituicoesEscala();
        state.escalaFiltroAtual = 'TODAS';
        document.querySelectorAll('.escala-filter-btn').forEach(b => b.classList.remove('active'));
        const btnAll = document.querySelector('.escala-filter-btn[data-escala-status="TODAS"]');
        if (btnAll) btnAll.classList.add('active');

        UI.renderizarEscalaSubstituicoes(state.escalaDataCache, 'TODAS');
        document.getElementById('escala-modal').style.display = 'block';
    } catch (err) {
        UI.showToast('Erro ao carregar escala de substituições: ' + err.message, 'error');
    }
}

function fecharModalEscalaSubstituicoes() {
    document.getElementById('escala-modal').style.display = 'none';
}
