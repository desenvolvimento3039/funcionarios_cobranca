// app.js - Gestão de Funcionários de Cobrança

const API_BASE = '/api';

// ─── Elementos DOM ────────────────────────────────────────────────────────────
const cobrancaTbody      = document.getElementById('cobranca-tbody');
const searchInput        = document.getElementById('search-input');
const btnSync            = document.getElementById('btn-sync');
const btnUploadExcel     = document.getElementById('btn-upload-excel');
const btnExportCsv       = document.getElementById('btn-export-csv');
const btnAddItem         = document.getElementById('btn-add-item');

const itemModal          = document.getElementById('item-modal');
const closeModal         = document.getElementById('close-modal');
const btnCancelModal     = document.getElementById('btn-cancel-modal');
const itemForm           = document.getElementById('item-form');
const modalTitle         = document.getElementById('modal-title');
const itemIdInput        = document.getElementById('item-id');

const itemTimeInput              = document.getElementById('item-time');
const timeSuggestions            = document.getElementById('time-suggestions');
const itemPaSelect               = document.getElementById('item-pa');
const itemCobradorBuscaInput     = document.getElementById('item-cobrador-busca');
const funcionarioSuggestions     = document.getElementById('funcionario-suggestions');
const itemMatriculaInput         = document.getElementById('item-matricula');
const itemCobradorInput          = document.getElementById('item-cobrador');
const itemFoneInput              = document.getElementById('item-fone');
const itemFilaInput              = document.getElementById('item-fila');
const filaSuggestions            = document.getElementById('fila-suggestions');
const filaDropdownToggle         = document.getElementById('fila-dropdown-toggle');
const itemStatusSelect           = document.getElementById('item-status');

const uploadExcelModal   = document.getElementById('upload-excel-modal');
const closeUploadModal   = document.getElementById('close-upload-modal');
const btnCancelUpload    = document.getElementById('btn-cancel-upload');
const uploadExcelForm    = document.getElementById('upload-excel-form');
const excelFileInput     = document.getElementById('excel-file-input');

const confirmModal       = document.getElementById('confirm-modal');
const closeConfirmModal  = document.getElementById('close-confirm-modal');
const btnCancelConfirm   = document.getElementById('btn-cancel-confirm');
const btnActionConfirm   = document.getElementById('btn-action-confirm');

const filterTime         = document.getElementById('filter-time');
const filterPa           = document.getElementById('filter-pa');
const filterStatus       = document.getElementById('filter-status');
const btnLimparFiltros   = document.getElementById('btn-limpar-filtros');

const syncResultModal    = document.getElementById('sync-result-modal');
const syncResultBody     = document.getElementById('sync-result-body');
const closeSyncResultModal = document.getElementById('close-sync-result-modal');
const btnCloseSyncResult = document.getElementById('btn-close-sync-result');

const avisoDescarte         = document.getElementById('aviso-descarte');
const btnDescartarConfirmar = document.getElementById('btn-descartar-confirmar');
const btnDescartarCancelar  = document.getElementById('btn-descartar-cancelar');

const avisoConfirmarSalvar      = document.getElementById('aviso-confirmar-salvar');
const saveConfirmSummaryDetails = document.getElementById('save-confirm-summary-details');
const btnConfirmarSalvarSim     = document.getElementById('btn-confirmar-salvar-sim');
const btnConfirmarSalvarNao     = document.getElementById('btn-confirmar-salvar-nao');
const itemModalFooter           = document.getElementById('item-modal-footer');

const pageStart        = document.getElementById('page-start');
const pageEnd          = document.getElementById('page-end');
const pageTotal        = document.getElementById('page-total');
const perPageSelect    = document.getElementById('per-page-select');
const btnPrevPage      = document.getElementById('btn-prev-page');
const btnNextPage      = document.getElementById('btn-next-page');
const pageCurrentLabel = document.getElementById('page-current-label');

const statTotal  = document.getElementById('stat-total');
const statTimes  = document.getElementById('stat-times');
const statPas    = document.getElementById('stat-pas');
const statFilas  = document.getElementById('stat-filas');

const btnToggleAnalytics  = document.getElementById('btn-toggle-analytics');
const chartsGridContent   = document.getElementById('charts-grid-content');

const toast = document.getElementById('toast');

const btnTutorial    = document.getElementById('btn-tutorial');
const tourOverlay    = document.getElementById('tour-overlay');
const tourCard       = document.getElementById('tour-card');
const tourStepBadge  = document.getElementById('tour-step-badge');
const tourTitle      = document.getElementById('tour-title');
const tourDescription = document.getElementById('tour-description');
const btnTourClose   = document.getElementById('btn-tour-close');
const btnTourSkip    = document.getElementById('btn-tour-skip');
const btnTourPrev    = document.getElementById('btn-tour-prev');
const btnTourNext    = document.getElementById('btn-tour-next');

// ─── Estado ───────────────────────────────────────────────────────────────────
let todosRegistros      = [];
let registrosFiltrados  = [];
let listaPAs            = [];  // [{ num_pa, nome_pa }]
let timesUnicos         = [];
let pasUnicos           = [];
let filasUnicas         = [];
let currentPage         = 1;
let itemsPerPage        = 25;
let totalServerItems    = 0;
let totalServerPages    = 1;
let idParaDeletar       = null;
let currentStepIndex    = 0;
let sortColumn          = 'id';
let sortDirection       = 'desc';
let formDirty           = false;
let _fecharModalForcado = false;
let payloadSalvarPendente = null;
let idSalvarPendente      = null;
let buscaDebounceTimer    = null;
let filterDebounceTimer   = null;

// Instâncias dos Gráficos Chart.js
let chartTimesInstance  = null;
let chartPasInstance    = null;
let chartStatusInstance = null;

// ─── Tutorial ─────────────────────────────────────────────────────────────────
const tourSteps = [
    {
        elementId: 'step-stats',
        title: '1. Resumo de Cobrança',
        description: 'Painel com contadores gerais: total de funcionários cadastrados, times de cobrança ativos, PAs atendidos e filas configuradas.',
        position: 'bottom'
    },
    {
        elementId: 'analytics-section',
        title: '2. Painel Gráfico & Analytics',
        description: 'Visualização dinâmica da distribuição de cobradores por time, PAs e status em tempo real.',
        position: 'bottom'
    },
    {
        elementId: 'step-search',
        title: '3. Busca e Filtros',
        description: 'Pesquise por cobrador, matrícula, fila ou time. Use os filtros de time, PA e status para refinar os resultados.',
        position: 'bottom'
    },
    {
        elementId: 'step-actions',
        title: '4. Cadastrar e Exportar',
        description: 'Adicione novos funcionários, faça upload da planilha Excel para carga em massa, ou exporte os dados em CSV.',
        position: 'bottom'
    },
    {
        elementId: 'step-table',
        title: '5. Tabela de Funcionários',
        description: 'Lista todos os cobradores cadastrados. Use os botões de ação para editar, inativar/ativar ou excluir registros.',
        position: 'center'
    }
];

// ─── Inicialização ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    carregarPAs();
    carregarCobranca();
    carregarAnalytics();
    setupEventListeners();
});

function setupEventListeners() {
    searchInput.addEventListener('input', () => {
        clearTimeout(filterDebounceTimer);
        filterDebounceTimer = setTimeout(() => {
            currentPage = 1;
            carregarCobranca();
        }, 300);
    });

    if (filterTime)   filterTime.addEventListener('change', () => { currentPage = 1; carregarCobranca(); });
    if (filterPa)     filterPa.addEventListener('change', () => { currentPage = 1; carregarCobranca(); });
    if (filterStatus) filterStatus.addEventListener('change', () => { currentPage = 1; carregarCobranca(); });
    if (btnLimparFiltros) btnLimparFiltros.addEventListener('click', limparFiltros);

    document.querySelectorAll('.th-sortable').forEach(th => {
        th.addEventListener('click', () => ordenarPor(th.dataset.col));
    });

    if (btnToggleAnalytics) {
        btnToggleAnalytics.addEventListener('click', () => {
            if (chartsGridContent.style.display === 'none') {
                chartsGridContent.style.display = 'grid';
                btnToggleAnalytics.innerHTML = '<i class="fa-solid fa-chevron-up"></i> Ocultar Gráficos';
            } else {
                chartsGridContent.style.display = 'none';
                btnToggleAnalytics.innerHTML = '<i class="fa-solid fa-chevron-down"></i> Exibir Gráficos';
            }
        });
    }

    if (closeSyncResultModal) closeSyncResultModal.addEventListener('click', () => syncResultModal.style.display = 'none');
    if (btnCloseSyncResult)   btnCloseSyncResult.addEventListener('click', () => syncResultModal.style.display = 'none');

    if (btnSync)        btnSync.addEventListener('click', sincronizarBancos);
    if (btnUploadExcel) btnUploadExcel.addEventListener('click', () => uploadExcelModal.style.display = 'block');
    if (closeUploadModal) closeUploadModal.addEventListener('click', () => uploadExcelModal.style.display = 'none');
    if (btnCancelUpload)  btnCancelUpload.addEventListener('click', () => uploadExcelModal.style.display = 'none');
    if (uploadExcelForm)  uploadExcelForm.addEventListener('submit', executarUploadExcel);

    if (btnExportCsv) {
        btnExportCsv.addEventListener('click', () => {
            window.location.href = `${API_BASE}/cobranca/exportar`;
        });
    }

    if (btnAddItem)    btnAddItem.addEventListener('click', () => abrirModalItem());
    if (closeModal)    closeModal.addEventListener('click', tentarFecharModal);
    if (btnCancelModal) btnCancelModal.addEventListener('click', tentarFecharModal);
    if (itemForm)      itemForm.addEventListener('submit', salvarItem);

    if (btnDescartarConfirmar) btnDescartarConfirmar.addEventListener('click', () => { _fecharModalForcado = true; fecharModal(); });
    if (btnDescartarCancelar)  btnDescartarCancelar.addEventListener('click', () => { avisoDescarte.style.display = 'none'; });

    if (btnConfirmarSalvarSim) btnConfirmarSalvarSim.addEventListener('click', executarSalvamentoConfirmado);
    if (btnConfirmarSalvarNao) btnConfirmarSalvarNao.addEventListener('click', ocultarConfirmacaoSalvar);

    if (itemForm) {
        itemForm.addEventListener('input', () => { formDirty = true; }, true);
        itemForm.addEventListener('change', () => { formDirty = true; }, true);
    }

    // Autocomplete de cobradores da tabela fun_funcionario
    if (itemCobradorBuscaInput) {
        itemCobradorBuscaInput.addEventListener('input', (e) => {
            clearTimeout(buscaDebounceTimer);
            buscaDebounceTimer = setTimeout(() => {
                buscarFuncionariosTabela(e.target.value);
            }, 300);
        });
        itemCobradorBuscaInput.addEventListener('focus', (e) => {
            buscarFuncionariosTabela(e.target.value);
        });
    }

    // Sugestões de time
    if (itemTimeInput) {
        itemTimeInput.addEventListener('input', () => mostrarSugestoesTime(itemTimeInput.value));
        itemTimeInput.addEventListener('focus', () => mostrarSugestoesTime(itemTimeInput.value));
    }

    // Sugestões de fila
    if (itemFilaInput) {
        itemFilaInput.addEventListener('input', () => mostrarSugestoesFila(itemFilaInput.value));
        itemFilaInput.addEventListener('focus', () => mostrarSugestoesFila(itemFilaInput.value));
    }
    if (filaDropdownToggle) {
        filaDropdownToggle.addEventListener('click', () => {
            if (filaSuggestions.style.display === 'block') {
                filaSuggestions.style.display = 'none';
            } else {
                mostrarSugestoesFila('');
            }
        });
    }

    // Fechar dropdowns ao clicar fora
    document.addEventListener('click', (e) => {
        if (funcionarioSuggestions && !itemCobradorBuscaInput.contains(e.target) && !funcionarioSuggestions.contains(e.target)) {
            funcionarioSuggestions.style.display = 'none';
        }
        if (filaSuggestions && !itemFilaInput.contains(e.target) && !filaSuggestions.contains(e.target) && !filaDropdownToggle.contains(e.target)) {
            filaSuggestions.style.display = 'none';
        }
        if (timeSuggestions && !itemTimeInput.contains(e.target) && !timeSuggestions.contains(e.target)) {
            timeSuggestions.style.display = 'none';
        }
    });

    if (closeConfirmModal) closeConfirmModal.addEventListener('click', fecharConfirmModal);
    if (btnCancelConfirm)  btnCancelConfirm.addEventListener('click', fecharConfirmModal);
    if (btnActionConfirm)  btnActionConfirm.addEventListener('click', executarExclusaoConfirmada);

    perPageSelect.addEventListener('change', (e) => {
        itemsPerPage = parseInt(e.target.value);
        currentPage = 1;
        carregarCobranca();
    });

    btnPrevPage.addEventListener('click', () => {
        if (currentPage > 1) { currentPage--; carregarCobranca(); }
    });
    btnNextPage.addEventListener('click', () => {
        if (currentPage < totalServerPages) { currentPage++; carregarCobranca(); }
    });

    if (btnTutorial) btnTutorial.addEventListener('click', iniciarTutorial);
    if (btnTourClose) btnTourClose.addEventListener('click', fecharTutorial);
    if (btnTourSkip)  btnTourSkip.addEventListener('click', fecharTutorial);
    if (btnTourPrev)  btnTourPrev.addEventListener('click', () => { if (currentStepIndex > 0) { currentStepIndex--; exibirPassoTutorial(); } });
    if (btnTourNext)  btnTourNext.addEventListener('click', () => {
        if (currentStepIndex < tourSteps.length - 1) { currentStepIndex++; exibirPassoTutorial(); } else { fecharTutorial(); }
    });
    if (tourOverlay) tourOverlay.addEventListener('click', fecharTutorial);

    window.addEventListener('scroll', () => {
        if (tourCard && tourCard.style.display === 'block') exibirPassoTutorial();
    }, { passive: true });
}

// ─── Carregamento de PAs da tabela inst_instituicao ─────────────────────────

async function carregarPAs() {
    try {
        const response = await fetch(`${API_BASE}/cobranca/pas`);
        if (!response.ok) throw new Error('Erro ao buscar PAs');
        listaPAs = await response.json();

        itemPaSelect.innerHTML = '<option value="">Selecione o PA...</option>';
        listaPAs.forEach(paObj => {
            const opt = document.createElement('option');
            opt.value = paObj.num_pa;
            opt.textContent = `PA ${paObj.num_pa} - ${paObj.nome_pa || ''}`;
            itemPaSelect.appendChild(opt);
        });
    } catch (err) {
        console.error('Falha ao carregar PAs da inst_instituicao:', err);
        itemPaSelect.innerHTML = '<option value="">Erro ao carregar PAs</option>';
    }
}

// ─── Busca de Cobradores na tabela fun_funcionario ────────────────────────────

async function buscarFuncionariosTabela(termo) {
    if (!funcionarioSuggestions) return;
    try {
        const url = termo && termo.trim()
            ? `${API_BASE}/cobranca/funcionarios-busca?q=${encodeURIComponent(termo.trim())}`
            : `${API_BASE}/cobranca/funcionarios-busca`;

        const response = await fetch(url);
        if (!response.ok) return;
        const funcionarios = await response.json();

        if (funcionarios.length === 0) {
            funcionarioSuggestions.innerHTML = `
                <div class="suggestion-header no-matches">
                    <i class="fa-solid fa-circle-info"></i>&nbsp; Nenhum funcionário encontrado na tabela fun_funcionario.
                </div>
            `;
            funcionarioSuggestions.style.display = 'block';
            return;
        }

        let html = `<div class="suggestion-header" style="color:#005c6d; background:#e0f2fe; border-bottom-color:#bae6fd;">
            <i class="fa-solid fa-users"></i>&nbsp; Selecione o funcionário (fun_funcionario):
        </div>`;

        funcionarios.forEach(f => {
            const matHL = highlightTexto(f.matricula.toString(), termo);
            const nomeHL = highlightTexto(f.cobrador, termo);
            html += `
                <div class="suggestion-item" onclick="selecionarFuncionarioTabela(${f.matricula}, '${escapeHtml(f.cobrador).replace(/'/g, "\\'")}')">
                    <div class="suggestion-item-main">
                        <span class="suggestion-item-nome">${nomeHL}</span>
                        <span class="suggestion-item-tags">
                            <span class="tag-enquadramento">Mat. ${matHL}</span>
                        </span>
                    </div>
                    <span class="suggestion-edit-btn" title="Selecionar">
                        <i class="fa-solid fa-check"></i>
                    </span>
                </div>
            `;
        });

        funcionarioSuggestions.innerHTML = html;
        funcionarioSuggestions.style.display = 'block';
    } catch (err) {
        console.error('Erro ao buscar funcionários na fun_funcionario:', err);
    }
}

function selecionarFuncionarioTabela(matricula, nome) {
    itemMatriculaInput.value = matricula;
    itemCobradorInput.value = nome;
    itemCobradorBuscaInput.value = `${matricula} - ${nome}`;
    funcionarioSuggestions.style.display = 'none';
    showToast(`Funcionário selecionado: Matrícula ${matricula}`, 'info');
}

// ─── Sugestões para Time e Fila ───────────────────────────────────────────────

function highlightTexto(texto, termo) {
    if (!termo) return escapeHtml(texto);
    const escaped = escapeHtml(texto.toString());
    const termoEscaped = escapeHtml(termo.toString());
    const regex = new RegExp(`(${termoEscaped.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return escaped.replace(regex, '<mark class="suggestion-highlight">$1</mark>');
}

function mostrarSugestoesTime(filtro) {
    const termo = (filtro || '').trim().toLowerCase();
    const filtrados = termo
        ? timesUnicos.filter(t => t.toLowerCase().includes(termo))
        : timesUnicos;

    if (filtrados.length === 0) {
        timeSuggestions.style.display = 'none';
        return;
    }

    let html = `<div class="suggestion-header" style="color:#005c6d; background:#e0f2fe; border-bottom-color:#bae6fd;">
        <i class="fa-solid fa-people-group"></i>&nbsp; Times cadastrados:
    </div>`;
    filtrados.slice(0, 10).forEach(t => {
        html += `
            <div class="suggestion-item suggestion-linha-item" onclick="selecionarTime('${escapeHtml(t).replace(/'/g, "\\'")}')">
                <span>${highlightTexto(t, termo)}</span>
                <i class="fa-solid fa-arrow-right-to-bracket" style="color:#94a3b8; font-size:11px;"></i>
            </div>
        `;
    });
    timeSuggestions.innerHTML = html;
    timeSuggestions.style.display = 'block';
}

function selecionarTime(valor) {
    itemTimeInput.value = valor;
    timeSuggestions.style.display = 'none';
    itemTimeInput.focus();
}

function mostrarSugestoesFila(filtro) {
    const termo = (filtro || '').trim().toLowerCase();
    const filtradas = termo
        ? filasUnicas.filter(f => f.toLowerCase().includes(termo))
        : filasUnicas;

    if (filtradas.length === 0) {
        filaSuggestions.innerHTML = `
            <div class="suggestion-header no-matches">
                <i class="fa-solid fa-circle-plus"></i>&nbsp; Nova fila — será cadastrada ao salvar.
            </div>
        `;
    } else {
        let html = `<div class="suggestion-header" style="color:#005c6d; background:#e0f2fe; border-bottom-color:#bae6fd;">
            <i class="fa-solid fa-list"></i>&nbsp; Filas cadastradas:
        </div>`;
        filtradas.slice(0, 10).forEach(f => {
            html += `
                <div class="suggestion-item suggestion-linha-item" onclick="selecionarFila('${escapeHtml(f).replace(/'/g, "\\'")}')">
                    <span>${highlightTexto(f, termo)}</span>
                    <i class="fa-solid fa-arrow-right-to-bracket" style="color:#94a3b8; font-size:11px;"></i>
                </div>
            `;
        });
        filaSuggestions.innerHTML = html;
    }
    filaSuggestions.style.display = 'block';
}

function selecionarFila(valor) {
    itemFilaInput.value = valor;
    filaSuggestions.style.display = 'none';
    itemFilaInput.focus();
}

// ─── Analytics / Painel Gráfico ───────────────────────────────────────────────

async function carregarAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/cobranca/stats`);
        if (!response.ok) return;
        const data = await response.json();
        renderizarGraficos(data);
    } catch (err) {
        console.error('Falha ao carregar dados de analytics:', err);
    }
}

function renderizarGraficos(data) {
    if (typeof Chart === 'undefined') return;

    // Colors Sicoob
    const colorsPrimary = ['#003641', '#005c6d', '#9FB100', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];

    // 1. Gráfico por Time (Doughnut)
    const ctxTimes = document.getElementById('chart-times');
    if (ctxTimes) {
        if (chartTimesInstance) chartTimesInstance.destroy();
        const labelsTimes = (data.por_time || []).map(x => x.label);
        const valuesTimes = (data.por_time || []).map(x => x.count);

        chartTimesInstance = new Chart(ctxTimes, {
            type: 'doughnut',
            data: {
                labels: labelsTimes,
                datasets: [{
                    data: valuesTimes,
                    backgroundColor: colorsPrimary,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    }

    // 2. Gráfico por PA (Bar)
    const ctxPas = document.getElementById('chart-pas');
    if (ctxPas) {
        if (chartPasInstance) chartPasInstance.destroy();
        const labelsPas = (data.por_pa || []).map(x => `PA ${x.pa}`);
        const valuesPas = (data.por_pa || []).map(x => x.count);

        chartPasInstance = new Chart(ctxPas, {
            type: 'bar',
            data: {
                labels: labelsPas,
                datasets: [{
                    label: 'Cobradores',
                    data: valuesPas,
                    backgroundColor: '#005c6d',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                    x: { ticks: { font: { size: 10 } } }
                }
            }
        });
    }

    // 3. Gráfico por Status (Pie)
    const ctxStatus = document.getElementById('chart-status');
    if (ctxStatus) {
        if (chartStatusInstance) chartStatusInstance.destroy();
        const statusMap = { 1: 'Ativos', 0: 'Inativos' };
        const labelsStatus = (data.por_status || []).map(x => statusMap[x.status] || 'Outro');
        const valuesStatus = (data.por_status || []).map(x => x.count);

        chartStatusInstance = new Chart(ctxStatus, {
            type: 'pie',
            data: {
                labels: labelsStatus,
                datasets: [{
                    data: valuesStatus,
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    }
}

// ─── Tutorial ─────────────────────────────────────────────────────────────────

function iniciarTutorial() {
    currentStepIndex = 0;
    tourOverlay.style.display = 'block';
    tourCard.style.display = 'block';
    exibirPassoTutorial();
}

function fecharTutorial() {
    tourOverlay.style.display = 'none';
    tourCard.style.display = 'none';
    removerDestaquesTour();
}

function removerDestaquesTour() {
    document.querySelectorAll('.tour-highlight').forEach(el => el.classList.remove('tour-highlight'));
    document.querySelectorAll('.tour-parent-highlight').forEach(el => el.classList.remove('tour-parent-highlight'));
}

function exibirPassoTutorial() {
    removerDestaquesTour();
    const step = tourSteps[currentStepIndex];
    const targetEl = document.getElementById(step.elementId);
    if (!targetEl) return;

    targetEl.classList.add('tour-highlight');
    const headerParent = targetEl.closest('.main-header');
    if (headerParent) headerParent.classList.add('tour-parent-highlight');

    if (step.elementId === 'step-table') {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    tourStepBadge.textContent = `Passo ${currentStepIndex + 1} de ${tourSteps.length}`;
    tourTitle.textContent = step.title;
    tourDescription.textContent = step.description;

    btnTourPrev.style.display = currentStepIndex === 0 ? 'none' : 'inline-flex';
    btnTourNext.innerHTML = currentStepIndex === tourSteps.length - 1
        ? 'Concluir <i class="fa-solid fa-check"></i>'
        : 'Próximo <i class="fa-solid fa-chevron-right"></i>';

    posicionarTourCard(targetEl, step.position);
    requestAnimationFrame(() => posicionarTourCard(targetEl, step.position));
}

function posicionarTourCard(targetEl, position) {
    const rect = targetEl.getBoundingClientRect();
    const cardWidth = 420;
    const cardHeight = 220;
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    let top = 0;
    let left = rect.left + (rect.width / 2) - (cardWidth / 2);

    if (left < 20) left = 20;
    if (left + cardWidth > viewportWidth - 20) left = viewportWidth - cardWidth - 20;

    if (position === 'center' || targetEl.id === 'step-table') {
        top = Math.max(100, Math.min(rect.top + 60, viewportHeight - cardHeight - 40));
    } else if (targetEl.id === 'btn-sync') {
        top = rect.bottom + 16;
        left = Math.max(20, Math.min(rect.right - cardWidth, viewportWidth - cardWidth - 20));
    } else if (position === 'bottom') {
        top = rect.bottom + 16;
        if (top + cardHeight > viewportHeight - 20) top = rect.top - cardHeight - 16;
    } else {
        top = rect.top - cardHeight - 16;
        if (top < 20) top = rect.bottom + 16;
    }

    if (top < 20) top = 80;
    if (top + cardHeight > viewportHeight - 20) top = viewportHeight - cardHeight - 20;

    tourCard.style.top = `${Math.round(top)}px`;
    tourCard.style.left = `${Math.round(left)}px`;
}

// ─── Carregamento de Dados (Paginação e Filtros Server-Side) ──────────────────

async function carregarCobranca() {
    try {
        const termo      = searchInput.value.trim();
        const timeFiltro = filterTime   ? filterTime.value   : '';
        const paFiltro   = filterPa     ? filterPa.value     : '';
        const statusFiltro = filterStatus ? filterStatus.value : '';

        const params = new URLSearchParams();
        params.append('page', currentPage);
        params.append('per_page', itemsPerPage);
        if (termo) params.append('search', termo);
        if (timeFiltro) params.append('time_cobranca', timeFiltro);
        if (paFiltro) params.append('pa', paFiltro);
        if (statusFiltro !== '') params.append('status', statusFiltro);
        if (sortColumn) {
            params.append('sort_by', sortColumn);
            params.append('sort_order', sortDirection);
        }

        const temFiltroAtivo = termo || timeFiltro || paFiltro || statusFiltro;
        if (btnLimparFiltros) btnLimparFiltros.style.display = temFiltroAtivo ? 'inline-flex' : 'none';

        const response = await fetch(`${API_BASE}/cobranca?${params.toString()}`);
        if (!response.ok) throw new Error('Erro ao carregar funcionários');

        const data = await response.json();

        if (Array.isArray(data)) {
            // Backwards compatibility se backend retornar lista direta
            todosRegistros = data;
            registrosFiltrados = data;
            totalServerItems = data.length;
            totalServerPages = 1;
        } else {
            registrosFiltrados = data.items || [];
            totalServerItems = data.total || 0;
            totalServerPages = data.total_pages || 1;
            currentPage = data.page || 1;
        }

        // Atualizar lista completa apenas para popular filtros dinâmicos se vazia
        if (timesUnicos.length === 0) {
            await carregarTudoParaFiltros();
        }

        atualizarEstatisticas();
        renderizarTabela();
    } catch (e) {
        console.error(e);
        cobrancaTbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <i class="fa-solid fa-triangle-exclamation"></i><br>
                    Erro ao carregar funcionários de cobrança.
                </td>
            </tr>
        `;
        showToast('Falha ao carregar dados', 'error');
    }
}

async function carregarTudoParaFiltros() {
    try {
        const response = await fetch(`${API_BASE}/cobranca`);
        if (!response.ok) return;
        const data = await response.json();
        const lista = Array.isArray(data) ? data : (data.items || []);
        todosRegistros = lista;
        atualizarDropdownsFiltros();
    } catch (err) {
        console.error(err);
    }
}

function atualizarDropdownsFiltros() {
    timesUnicos = [...new Set(todosRegistros.map(r => r.times_cobranca).filter(Boolean))].sort();
    pasUnicos   = [...new Set(todosRegistros.map(r => r.num_pa))].sort((a, b) => a - b);
    filasUnicas = [...new Set(todosRegistros.map(r => r.fila).filter(Boolean))].sort();

    if (filterTime) {
        const valAtual = filterTime.value;
        filterTime.innerHTML = '<option value="">Todos os Times</option>';
        timesUnicos.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t;
            opt.textContent = t;
            filterTime.appendChild(opt);
        });
        filterTime.value = valAtual;
    }

    if (filterPa) {
        const valAtual = filterPa.value;
        filterPa.innerHTML = '<option value="">Todos os PAs</option>';
        pasUnicos.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            const paObj = listaPAs.find(x => x.num_pa === p);
            opt.textContent = paObj ? `PA ${p} - ${paObj.nome_pa}` : `PA ${p}`;
            filterPa.appendChild(opt);
        });
        filterPa.value = valAtual;
    }
}

function atualizarEstatisticas() {
    if (statTotal) statTotal.textContent = totalServerItems;
    if (statTimes) statTimes.textContent = timesUnicos.length;
    if (statPas)   statPas.textContent   = pasUnicos.length;
    if (statFilas) statFilas.textContent = filasUnicas.length;
}

// ─── Filtros ──────────────────────────────────────────────────────────────────

function limparFiltros() {
    searchInput.value = '';
    if (filterTime)   filterTime.value = '';
    if (filterPa)     filterPa.value = '';
    if (filterStatus) filterStatus.value = '';
    currentPage = 1;
    carregarCobranca();
}

// ─── Ordenação ────────────────────────────────────────────────────────────────

function ordenarPor(col) {
    if (sortColumn === col) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = col;
        sortDirection = col === 'id' ? 'desc' : 'asc';
    }
    atualizarIconesSort();
    carregarCobranca();
}

function atualizarIconesSort() {
    document.querySelectorAll('.th-sortable').forEach(th => {
        const icon = th.querySelector('.sort-icon');
        if (!icon) return;
        th.classList.remove('sort-asc', 'sort-desc');
        icon.className = 'fa-solid fa-sort sort-icon';
        if (th.dataset.col === sortColumn) {
            th.classList.add(sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
            icon.className = `fa-solid fa-sort-${sortDirection === 'asc' ? 'up' : 'down'} sort-icon sort-icon-active`;
        }
    });
}

// ─── Renderização da Tabela ───────────────────────────────────────────────────

function renderizarTabela() {
    if (registrosFiltrados.length === 0) {
        cobrancaTbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <i class="fa-solid fa-folder-open"></i><br>
                    Nenhum funcionário de cobrança encontrado.
                </td>
            </tr>
        `;
        pageStart.textContent = '0';
        pageEnd.textContent = '0';
        pageTotal.textContent = '0';
        pageCurrentLabel.textContent = 'Página 0 de 0';
        btnPrevPage.disabled = true;
        btnNextPage.disabled = true;
        return;
    }

    const startIdx = (currentPage - 1) * itemsPerPage + 1;
    const endIdx   = Math.min(currentPage * itemsPerPage, totalServerItems);

    cobrancaTbody.innerHTML = '';
    registrosFiltrados.forEach(r => {
        try {
            const tr = document.createElement('tr');
            const isAtivo = r.status !== 0 && r.status !== '0';
            if (!isAtivo) tr.classList.add('row-inactive');

            const statusBadge = isAtivo
                ? '<span class="badge-status-active"><i class="fa-solid fa-circle-check"></i> Ativo</span>'
                : '<span class="badge-status-inactive"><i class="fa-solid fa-circle-xmark"></i> Inativo</span>';

            const toggleBtn = isAtivo
                ? `<button class="btn btn-secondary btn-icon btn-toggle-inativar" onclick="alternarStatus(${r.id}, 0)" title="Inativar">
                        <i class="fa-solid fa-toggle-on" style="color: #10b981; font-size: 16px;"></i>
                   </button>`
                : `<button class="btn btn-secondary btn-icon btn-toggle-ativar" onclick="alternarStatus(${r.id}, 1)" title="Ativar">
                        <i class="fa-solid fa-toggle-off" style="color: #94a3b8; font-size: 16px;"></i>
                   </button>`;

            const timeStr = r.times_cobranca ? String(r.times_cobranca) : '';
            const timeBadge = (timeStr.trim() !== '')
                ? `<span class="badge-time">${escapeHtml(timeStr)}</span>`
                : `<span class="badge-time-empty">—</span>`;

            const paObj = listaPAs.find(x => x.num_pa === r.num_pa);
            const paTexto = paObj ? `PA ${r.num_pa} - ${paObj.nome_pa}` : `PA ${r.num_pa}`;

            tr.innerHTML = `
                <td><span class="badge-priority">${r.id}</span></td>
                <td>${timeBadge}</td>
                <td><span class="badge-pa-num" title="${escapeHtml(paTexto)}">PA ${r.num_pa}</span></td>
                <td><span class="badge-matricula">${r.matricula}</span></td>
                <td><strong>${escapeHtml(r.cobrador)}</strong></td>
                <td><span class="badge-fila">${escapeHtml(r.fila)}</span></td>
                <td><span class="fone-text">${escapeHtml(r.telefone || '-')}</span></td>
                <td>${statusBadge}</td>
                <td>
                    <div class="row-actions">
                        ${toggleBtn}
                        <button class="btn btn-secondary btn-icon" onclick="editarItem(${r.id})" title="Editar">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-danger btn-icon" onclick="confirmarExclusao(${r.id})" title="Excluir">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            `;
            cobrancaTbody.appendChild(tr);
        } catch (err) {
            console.error('Erro ao renderizar linha:', r, err);
        }
    });

    pageStart.textContent = startIdx;
    pageEnd.textContent = endIdx;
    pageTotal.textContent = totalServerItems;
    pageCurrentLabel.textContent = `Página ${currentPage} de ${totalServerPages}`;
    btnPrevPage.disabled = currentPage === 1;
    btnNextPage.disabled = currentPage === totalServerPages;
}

// ─── Modal Criar/Editar ───────────────────────────────────────────────────────

function abrirModalItem(item = null) {
    itemForm.reset();
    formDirty = false;
    _fecharModalForcado = false;
    ocultarConfirmacaoSalvar();
    if (avisoDescarte) avisoDescarte.style.display = 'none';
    if (funcionarioSuggestions) funcionarioSuggestions.style.display = 'none';
    if (timeSuggestions) timeSuggestions.style.display = 'none';
    if (filaSuggestions) filaSuggestions.style.display = 'none';

    if (item) {
        modalTitle.textContent = 'Editar Funcionário de Cobrança';
        itemIdInput.value          = item.id;
        itemTimeInput.value        = item.times_cobranca;
        itemPaSelect.value         = item.num_pa;
        itemMatriculaInput.value   = item.matricula;
        itemCobradorInput.value    = item.cobrador;
        if (itemCobradorBuscaInput) itemCobradorBuscaInput.value = `${item.matricula} - ${item.cobrador}`;
        itemFilaInput.value        = item.fila;
        itemFoneInput.value        = item.telefone || '';
        if (itemStatusSelect) itemStatusSelect.value = (item.status === 0 || item.status === '0') ? '0' : '1';
    } else {
        modalTitle.textContent = 'Novo Funcionário de Cobrança';
        itemIdInput.value = '';
        if (itemCobradorBuscaInput) itemCobradorBuscaInput.value = '';
        if (itemStatusSelect) itemStatusSelect.value = '1';
    }

    setTimeout(() => { formDirty = false; }, 50);
    itemModal.style.display = 'block';
    setTimeout(() => itemTimeInput.focus(), 100);
}

function tentarFecharModal() {
    if (formDirty && !_fecharModalForcado) {
        if (avisoDescarte) avisoDescarte.style.display = 'flex';
        return;
    }
    fecharModal();
}

function fecharModal() {
    itemModal.style.display = 'none';
    if (funcionarioSuggestions) funcionarioSuggestions.style.display = 'none';
    if (timeSuggestions) timeSuggestions.style.display = 'none';
    if (filaSuggestions) filaSuggestions.style.display = 'none';
    if (avisoDescarte) avisoDescarte.style.display = 'none';
    ocultarConfirmacaoSalvar();
    formDirty = false;
    _fecharModalForcado = false;
}

function ocultarConfirmacaoSalvar() {
    if (avisoConfirmarSalvar) avisoConfirmarSalvar.style.display = 'none';
    if (itemModalFooter) itemModalFooter.style.display = 'flex';
    payloadSalvarPendente = null;
    idSalvarPendente = null;
}

function editarItem(id) {
    const item = registrosFiltrados.find(r => r.id === id) || todosRegistros.find(r => r.id === id);
    if (item) abrirModalItem(item);
}

// ─── Salvar ───────────────────────────────────────────────────────────────────

function salvarItem(e) {
    e.preventDefault();

    const id = itemIdInput.value;
    const payload = {
        times_cobranca: itemTimeInput.value.trim(),
        num_pa:         parseInt(itemPaSelect.value),
        matricula:      parseInt(itemMatriculaInput.value),
        cobrador:       itemCobradorInput.value.trim(),
        fila:           itemFilaInput.value.trim(),
        telefone:       itemFoneInput.value.trim(),
        status:         itemStatusSelect ? parseInt(itemStatusSelect.value) : 1
    };

    if (!payload.times_cobranca) { showToast('Informe o Time de Cobrança.', 'error'); return; }
    if (!payload.num_pa || payload.num_pa < 1) { showToast('Selecione um PA da tabela inst_instituicao.', 'error'); return; }
    if (!payload.matricula || payload.matricula < 1) { showToast('Informe/Selecione uma Matrícula válida.', 'error'); return; }
    if (!payload.cobrador) { showToast('Informe/Selecione o nome do Cobrador.', 'error'); return; }
    if (!payload.fila) { showToast('Informe a Fila de Cobrança.', 'error'); return; }

    payloadSalvarPendente = payload;
    idSalvarPendente = id;

    const paObj = listaPAs.find(x => x.num_pa === payload.num_pa);
    const paLabel = paObj ? `PA ${payload.num_pa} - ${paObj.nome_pa}` : `PA ${payload.num_pa}`;

    if (saveConfirmSummaryDetails) {
        saveConfirmSummaryDetails.innerHTML = `
            <div class="save-confirm-summary-item"><strong>Time:</strong> ${escapeHtml(payload.times_cobranca)}</div>
            <div><strong>PA:</strong> ${escapeHtml(paLabel)}</div>
            <div><strong>Matrícula:</strong> ${payload.matricula}</div>
            <div><strong>Cobrador:</strong> ${escapeHtml(payload.cobrador)}</div>
            <div><strong>Fila:</strong> ${escapeHtml(payload.fila)}</div>
            <div><strong>Telefone:</strong> ${escapeHtml(payload.telefone || '(não informado)')}</div>
            <div><strong>Status:</strong> ${payload.status === 1 ? 'Ativo' : 'Inativo'}</div>
        `;
    }

    if (avisoDescarte) avisoDescarte.style.display = 'none';
    if (avisoConfirmarSalvar) avisoConfirmarSalvar.style.display = 'block';
    if (itemModalFooter) itemModalFooter.style.display = 'none';
}

async function executarSalvamentoConfirmado() {
    if (!payloadSalvarPendente) return;
    const payload = payloadSalvarPendente;
    const id = idSalvarPendente;

    try {
        const url    = id ? `${API_BASE}/cobranca/${id}` : `${API_BASE}/cobranca`;
        const method = id ? 'PUT' : 'POST';
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Falha ao salvar funcionário');
        }
        _fecharModalForcado = true;
        fecharModal();
        showToast(id ? 'Funcionário atualizado com sucesso!' : 'Funcionário cadastrado em fun_funcionarios_cobranca!', 'success');
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        console.error(err);
        showToast(err.message || 'Falha na operação', 'error');
    }
}

// ─── Status Toggle ────────────────────────────────────────────────────────────

async function alternarStatus(id, novoStatus) {
    const acao = novoStatus === 1 ? 'Ativando' : 'Inativando';
    try {
        showToast(`${acao} funcionário...`, 'info');
        const response = await fetch(`${API_BASE}/cobranca/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Falha ao ${acao.toLowerCase()} funcionário`);
        }
        showToast(`Funcionário ${novoStatus === 1 ? 'ativado' : 'inativado'} com sucesso!`, 'success');
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        console.error(err);
        showToast(err.message || 'Falha na operação', 'error');
    }
}

// ─── Exclusão ─────────────────────────────────────────────────────────────────

function confirmarExclusao(id) {
    idParaDeletar = id;
    confirmModal.style.display = 'block';
}

function fecharConfirmModal() {
    confirmModal.style.display = 'none';
    idParaDeletar = null;
}

async function executarExclusaoConfirmada() {
    if (!idParaDeletar) return;
    const id = idParaDeletar;
    fecharConfirmModal();
    try {
        const response = await fetch(`${API_BASE}/cobranca/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Erro ao excluir funcionário');
        showToast('Funcionário excluído de fun_funcionarios_cobranca!', 'success');
        carregarCobranca();
        carregarAnalytics();
    } catch (e) {
        console.error(e);
        showToast('Falha ao excluir funcionário', 'error');
    }
}

// ─── Sincronização ────────────────────────────────────────────────────────────

async function sincronizarBancos() {
    try {
        showToast('Sincronizando tabela fun_funcionarios_cobranca nas bases...', 'info');
        const response = await fetch(`${API_BASE}/cobranca/sincronizar`, { method: 'POST' });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Falha na sincronização');
        }
        const data = await response.json();
        carregarCobranca();
        carregarAnalytics();

        if (syncResultModal && syncResultBody && data.detalhes) {
            const det = data.detalhes;
            let html = `
                <div class="sync-result-summary">
                    <p class="sync-result-msg"><i class="fa-solid fa-circle-check" style="color:#10b981;"></i> Sincronização concluída com sucesso!</p>
                    <p style="color:#64748b; font-size:13px; margin-top:4px;">${escapeHtml(data.message || '')}</p>
                </div>
                <table class="sync-result-table">
                    <thead>
                        <tr><th>Banco</th><th>Inseridos</th><th>Atualizados</th><th>Total na fun_funcionarios_cobranca</th></tr>
                    </thead>
                    <tbody>
            `;
            Object.entries(det).forEach(([db, stats]) => {
                html += `
                    <tr>
                        <td><strong>${escapeHtml(db)}</strong></td>
                        <td class="sync-cell-inserted">${stats.inserted ?? '-'}</td>
                        <td class="sync-cell-updated">${stats.updated ?? '-'}</td>
                        <td>${stats.total ?? '-'}</td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;
            syncResultBody.innerHTML = html;
            syncResultModal.style.display = 'block';
        } else {
            showToast('Sincronização concluída!', 'success');
        }
    } catch (e) {
        console.error(e);
        showToast(e.message || 'Falha na sincronização', 'error');
    }
}

// ─── Upload Excel ─────────────────────────────────────────────────────────────

async function executarUploadExcel(e) {
    e.preventDefault();
    const files = excelFileInput.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('file', files[0]);

    try {
        showToast('Enviando planilha Excel...', 'info');
        uploadExcelModal.style.display = 'none';

        const response = await fetch(`${API_BASE}/cobranca/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Falha no upload');
        }

        const data = await response.json();
        showToast(data.message || 'Planilha processada com sucesso!', 'success');
        uploadExcelForm.reset();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        console.error(err);
        showToast(err.message || 'Falha no upload da planilha', 'error');
    }
}

// ─── Utilitários ──────────────────────────────────────────────────────────────

function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 4000);
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
