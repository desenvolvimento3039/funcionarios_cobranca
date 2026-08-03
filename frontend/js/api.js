// api.js - Funções de comunicação com o backend
const API_BASE = '/api';

async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Erro na requisição');
    }
    return response.json();
}

const api = {
    getPAs: () => apiFetch(`${API_BASE}/cobranca/pas`),
    getFuncionariosBusca: (termo) => {
        const url = termo && termo.trim() 
            ? `${API_BASE}/cobranca/funcionarios-busca?q=${encodeURIComponent(termo.trim())}` 
            : `${API_BASE}/cobranca/funcionarios-busca`;
        return apiFetch(url);
    },
    getStats: () => apiFetch(`${API_BASE}/cobranca/stats`),
    getCobranca: (params) => apiFetch(`${API_BASE}/cobranca?${params.toString()}`),
    getCobrancaAll: () => apiFetch(`${API_BASE}/cobranca`),
    saveCobranca: (id, payload) => {
        const url = id ? `${API_BASE}/cobranca/${id}` : `${API_BASE}/cobranca`;
        const method = id ? 'PUT' : 'POST';
        return apiFetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    },
    toggleStatus: (id, novoStatus) => {
        return apiFetch(`${API_BASE}/cobranca/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });
    },
    deleteCobranca: (id) => apiFetch(`${API_BASE}/cobranca/${id}`, { method: 'DELETE' }),
    syncDb: () => apiFetch(`${API_BASE}/cobranca/sincronizar`, { method: 'POST' }),
    uploadExcel: (formData) => {
        return apiFetch(`${API_BASE}/cobranca/upload`, {
            method: 'POST',
            body: formData
        });
    },
    getFilasSemCobradores: () => apiFetch(`${API_BASE}/cobranca/filas-sem-cobradores`),
    saveSubstituicaoDireta: (payload) => {
        return apiFetch(`${API_BASE}/cobranca/substituicao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    }
};
