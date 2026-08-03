// app.js - Lógica principal e orquestração

window.appContext = {};

const state = {
    todosRegistros: [],
    registrosFiltrados: [],
    listaPAs: [],
    timesUnicos: [],
    pasUnicos: [],
    filasUnicas: [],
    filasSemCobrador: [],
    currentPage: 1,
    itemsPerPage: 25,
    totalServerItems: 0,
    totalServerPages: 1,
    sortColumn: 'id',
    sortDirection: 'desc',
    idParaDeletar: null
};

// ─── Inicialização ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await carregarPAs();
    await carregarCobranca();
    await carregarAnalytics();
    setupEventListeners();
});

async function carregarPAs() {
    try {
        state.listaPAs = await api.getPAs();
        const sel = document.getElementById('item-pa');
        if (sel) {
            sel.innerHTML = '<option value="">Selecione o PA...</option>';
            state.listaPAs.forEach(pa => {
                const opt = document.createElement('option');
                opt.value = pa.num_pa;
                opt.textContent = `PA ${pa.num_pa} - ${pa.nome_pa || ''}`;
                sel.appendChild(opt);
            });
        }
    } catch (e) { console.error('Erro ao carregar PAs', e); }
}

async function carregarAnalytics() {
    try {
        const data = await api.getStats();
        UI.renderizarGraficos(data);
    } catch (e) { console.error('Erro ao carregar stats', e); }
}

async function carregarCobranca() {
    try {
        const termo = document.getElementById('search-input')?.value.trim() || '';
        const params = new URLSearchParams({
            page: state.currentPage,
            per_page: state.itemsPerPage,
            sort_by: state.sortColumn,
            sort_order: state.sortDirection
        });
        if (termo) params.append('search', termo);
        
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

        // Popula o select de "Substituindo quem" no cadastro normal
        const subDe = document.getElementById('item-substituto-de');
        if (subDe) {
            subDe.innerHTML = '<option value="">Selecione o cobrador original...</option>';
            state.todosRegistros.filter(r => r.status === 1 || r.status === '1').forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = `${r.matricula} - ${r.cobrador} (PA ${r.num_pa})`;
                subDe.appendChild(opt);
            });
        }

        // Busca filas sem cobradores
        try {
            state.filasSemCobrador = await api.getFilasSemCobradores();
        } catch (e) {
            console.error('Erro ao buscar filas sem cobrador', e);
            state.filasSemCobrador = [];
        }

        UI.renderizarEstatisticas(state.totalServerItems, state.timesUnicos.length, state.pasUnicos.length, state.filasUnicas.length, state.filasSemCobrador.length);
        UI.renderizarTabela(state.registrosFiltrados, state.totalServerItems, state.currentPage, state.totalServerPages, state.itemsPerPage, 
            (state.currentPage - 1) * state.itemsPerPage + 1, Math.min(state.currentPage * state.itemsPerPage, state.totalServerItems), state.listaPAs, window.appContext);
    } catch (e) {
        console.error('Erro ao carregar cobrança', e);
        UI.showToast('Erro ao carregar dados da tabela', 'error');
    }
}

function setupEventListeners() {
    document.getElementById('search-input')?.addEventListener('input', () => { state.currentPage = 1; carregarCobranca(); });
    document.getElementById('per-page-select')?.addEventListener('change', (e) => { state.itemsPerPage = parseInt(e.target.value); state.currentPage = 1; carregarCobranca(); });
    document.getElementById('btn-prev-page')?.addEventListener('click', () => { if(state.currentPage > 1){ state.currentPage--; carregarCobranca(); } });
    document.getElementById('btn-next-page')?.addEventListener('click', () => { if(state.currentPage < state.totalServerPages){ state.currentPage++; carregarCobranca(); } });
    
    document.getElementById('btn-add-item')?.addEventListener('click', () => abrirModalItem());
    document.getElementById('close-modal')?.addEventListener('click', fecharModalItem);
    document.getElementById('btn-cancel-modal')?.addEventListener('click', fecharModalItem);
    document.getElementById('item-form')?.addEventListener('submit', salvarItem);

    document.getElementById('close-confirm-modal')?.addEventListener('click', fecharConfirmModal);
    document.getElementById('btn-cancel-confirm')?.addEventListener('click', fecharConfirmModal);
    document.getElementById('btn-action-confirm')?.addEventListener('click', executarExclusaoConfirmada);

    document.getElementById('btn-sync')?.addEventListener('click', sincronizarBancos);
    
    // Substituto Checkbox no cadastro normal
    const chkSub = document.getElementById('item-is-substituto');
    const fieldsSub = document.getElementById('substituto-fields');
    if (chkSub && fieldsSub) {
        chkSub.addEventListener('change', (e) => {
            fieldsSub.style.display = e.target.checked ? 'block' : 'none';
        });
    }

    // Botão Adicionar Substituto Direto
    document.getElementById('btn-add-substituto')?.addEventListener('click', abrirModalSubstitutoDireto);
    document.getElementById('close-sub-dir-modal')?.addEventListener('click', fecharModalSubstitutoDireto);
    document.getElementById('btn-cancel-sub-dir')?.addEventListener('click', fecharModalSubstitutoDireto);
    document.getElementById('sub-dir-form')?.addEventListener('submit', salvarSubstitutoDireto);

    // Card de Filas Sem Cobradores
    document.getElementById('card-filas-sem-cobrador')?.addEventListener('click', abrirModalFilasSemCobrador);
    document.getElementById('close-filas-sem-cob-modal')?.addEventListener('click', fecharModalFilasSemCobrador);
    document.getElementById('btn-close-filas-sem-cob')?.addEventListener('click', fecharModalFilasSemCobrador);
}

function abrirModalItem(item = null) {
    document.getElementById('item-form').reset();
    document.getElementById('substituto-fields').style.display = 'none';
    
    if (item) {
        document.getElementById('modal-title').textContent = 'Editar Funcionário';
        document.getElementById('item-id').value = item.id;
        document.getElementById('item-time').value = item.times_cobranca || '';
        document.getElementById('item-pa').value = item.num_pa || '';
        document.getElementById('item-matricula').value = item.matricula || '';
        document.getElementById('item-cobrador').value = item.cobrador || '';
        document.getElementById('item-fila').value = item.fila || '';
        document.getElementById('item-fone').value = item.telefone || '';
        document.getElementById('item-status').value = (item.status === 0) ? '0' : '1';
        
        document.getElementById('item-is-substituto').disabled = true;
    } else {
        document.getElementById('modal-title').textContent = 'Novo Funcionário';
        document.getElementById('item-id').value = '';
        document.getElementById('item-is-substituto').disabled = false;
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
    
    const payload = {
        times_cobranca: document.getElementById('item-time').value.trim(),
        num_pa: parseInt(document.getElementById('item-pa').value),
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
        UI.showToast(id ? 'Funcionário atualizado!' : 'Funcionário cadastrado!', 'success');
        fecharModalItem();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── Modal Substituto Direto ──────────────────────────────────────────────────
function abrirModalSubstitutoDireto() {
    const subSel = document.getElementById('sub-dir-substituto');
    const origSel = document.getElementById('sub-dir-original');
    document.getElementById('sub-dir-form').reset();
    
    if (subSel && origSel) {
        const optionHtml = '<option value="">Selecione o cobrador...</option>';
        subSel.innerHTML = optionHtml;
        origSel.innerHTML = optionHtml;
        
        state.todosRegistros.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.id;
            opt.textContent = `${r.matricula} - ${r.cobrador} (${r.times_cobranca} - PA ${r.num_pa})`;
            
            subSel.appendChild(opt.cloneNode(true));
            origSel.appendChild(opt);
        });
    }
    
    document.getElementById('substituto-direto-modal').style.display = 'block';
}

function fecharModalSubstitutoDireto() {
    document.getElementById('substituto-direto-modal').style.display = 'none';
}

async function salvarSubstitutoDireto(e) {
    e.preventDefault();
    const payload = {
        substituto_id: parseInt(document.getElementById('sub-dir-substituto').value),
        original_id: parseInt(document.getElementById('sub-dir-original').value),
        data_inicio: document.getElementById('sub-dir-inicio').value,
        data_fim: document.getElementById('sub-dir-fim').value
    };

    if (payload.substituto_id === payload.original_id) {
        UI.showToast('O substituto não pode ser igual ao funcionário original.', 'error');
        return;
    }

    try {
        await api.saveSubstituicaoDireta(payload);
        UI.showToast('Substituição agendada com sucesso!', 'success');
        fecharModalSubstitutoDireto();
        carregarCobranca();
        carregarAnalytics();
    } catch (err) {
        UI.showToast(err.message, 'error');
    }
}

// ─── Modal Filas sem Cobrador ─────────────────────────────────────────────────
function abrirModalFilasSemCobrador() {
    UI.renderizarFilasSemCobrador(state.filasSemCobrador, adicionarCobradorFilaCallback);
    document.getElementById('filas-sem-cobrador-modal').style.display = 'block';
}

function fecharModalFilasSemCobrador() {
    document.getElementById('filas-sem-cobrador-modal').style.display = 'none';
}

function adicionarCobradorFilaCallback(nomeFila) {
    fecharModalFilasSemCobrador();
    abrirModalItem();
    const inputFila = document.getElementById('item-fila');
    if (inputFila) {
        inputFila.value = nomeFila;
        // Simula interação para ativar dirty checker ou autocomplete
        inputFila.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

appContext.editarItem = (id) => {
    const item = state.registrosFiltrados.find(r => r.id === id) || state.todosRegistros.find(r => r.id === id);
    if (item) abrirModalItem(item);
};

appContext.alternarStatus = async (id, status) => {
    try {
        await api.toggleStatus(id, status);
        UI.showToast('Status alterado!', 'success');
        carregarCobranca();
    } catch (e) {
        UI.showToast('Erro ao alterar status', 'error');
    }
};

appContext.confirmarExclusao = (id) => {
    state.idParaDeletar = id;
    document.getElementById('confirm-modal').style.display = 'block';
};

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
