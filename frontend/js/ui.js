// ui.js - Funções de Manipulação da Interface do Usuário

const UI = {
    cobrancaTbody: document.getElementById('cobranca-tbody'),
    pageStart: document.getElementById('page-start'),
    pageEnd: document.getElementById('page-end'),
    pageTotal: document.getElementById('page-total'),
    pageCurrentLabel: document.getElementById('page-current-label'),
    btnPrevPage: document.getElementById('btn-prev-page'),
    btnNextPage: document.getElementById('btn-next-page'),
    toast: document.getElementById('toast'),
    
    // Stats
    statTotal: document.getElementById('stat-total'),
    statTimes: document.getElementById('stat-times'),
    statPas: document.getElementById('stat-pas'),
    statFilas: document.getElementById('stat-filas'),

    // Modais
    syncResultModal: document.getElementById('sync-result-modal'),
    syncResultBody: document.getElementById('sync-result-body'),

    showToast: (message, type = 'info') => {
        UI.toast.textContent = message;
        UI.toast.className = `toast ${type} show`;
        setTimeout(() => { UI.toast.className = 'toast'; }, 4000);
    },

    escapeHtml: (str) => {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    renderizarEstatisticas: (totalItems, timesCount, pasCount, filasCount, filasSemCobradorCount) => {
        if (UI.statTotal) UI.statTotal.textContent = totalItems;
        if (UI.statTimes) UI.statTimes.textContent = timesCount;
        if (UI.statPas)   UI.statPas.textContent   = pasCount;
        if (UI.statFilas) UI.statFilas.textContent = filasCount;
        const elSemCob = document.getElementById('stat-filas-sem-cobrador');
        if (elSemCob) elSemCob.textContent = filasSemCobradorCount;
    },

    renderizarFilasSemCobrador: (filas, callbackAdicionar) => {
        const tbody = document.getElementById('filas-sem-cob-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (filas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="2" style="text-align:center; padding: 12px; color: #64748b;">Nenhuma fila sem cobrador identificada.</td></tr>`;
            return;
        }
        filas.forEach(fila => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #e2e8f0';
            
            const tdFila = document.createElement('td');
            tdFila.style.padding = '8px';
            tdFila.innerHTML = `<strong>${UI.escapeHtml(fila)}</strong>`;
            
            const tdAcao = document.createElement('td');
            tdAcao.style.padding = '8px';
            tdAcao.style.textAlign = 'right';
            
            const btn = document.createElement('button');
            btn.className = 'btn btn-success btn-sm';
            btn.innerHTML = `<i class="fa-solid fa-plus"></i> Adicionar Cobrador`;
            btn.addEventListener('click', () => {
                callbackAdicionar(fila);
            });
            
            tdAcao.appendChild(btn);
            tr.appendChild(tdFila);
            tr.appendChild(tdAcao);
            tbody.appendChild(tr);
        });
    },

    renderizarTabela: (registros, totalItems, currentPage, totalPages, itemsPerPage, startIdx, endIdx, listaPAs, context) => {
        if (!registros || registros.length === 0) {
            UI.cobrancaTbody.innerHTML = `<tr><td colspan="9" class="empty-state">
                <i class="fa-solid fa-folder-open"></i><br>Nenhum funcionário de cobrança encontrado.</td></tr>`;
            UI.pageStart.textContent = '0';
            UI.pageEnd.textContent = '0';
            UI.pageTotal.textContent = '0';
            UI.pageCurrentLabel.textContent = 'Página 0 de 0';
            UI.btnPrevPage.disabled = true;
            UI.btnNextPage.disabled = true;
            return;
        }

        UI.cobrancaTbody.innerHTML = '';
        registros.forEach(r => {
            const tr = document.createElement('tr');
            const isAtivo = r.status !== 0 && r.status !== '0';
            if (!isAtivo) tr.classList.add('row-inactive');

            const statusBadge = isAtivo
                ? '<span class="badge-status-active"><i class="fa-solid fa-circle-check"></i> Ativo</span>'
                : '<span class="badge-status-inactive"><i class="fa-solid fa-circle-xmark"></i> Inativo</span>';

            const toggleBtn = isAtivo
                ? `<button class="btn btn-secondary btn-icon btn-toggle-inativar" onclick="appContext.alternarStatus(${r.id}, 0)" title="Inativar">
                        <i class="fa-solid fa-toggle-on" style="color: #10b981; font-size: 16px;"></i></button>`
                : `<button class="btn btn-secondary btn-icon btn-toggle-ativar" onclick="appContext.alternarStatus(${r.id}, 1)" title="Ativar">
                        <i class="fa-solid fa-toggle-off" style="color: #94a3b8; font-size: 16px;"></i></button>`;

            const timeStr = r.times_cobranca ? String(r.times_cobranca) : '';
            const timeBadge = (timeStr.trim() !== '') ? `<span class="badge-time">${UI.escapeHtml(timeStr)}</span>` : `<span class="badge-time-empty">—</span>`;
            
            let cobradorLabel = UI.escapeHtml(r.cobrador);
            if (r.substituto_de_id) {
                cobradorLabel += ` <span style="font-size: 10px; background: #fef08a; padding: 2px 6px; border-radius: 4px; color: #854d0e; font-weight: bold; margin-left: 4px;"><i class="fa-solid fa-user-clock"></i> Substituto</span>`;
            }

            const paObj = listaPAs.find(x => x.num_pa === r.num_pa);
            const paTexto = paObj ? `PA ${r.num_pa} - ${paObj.nome_pa}` : `PA ${r.num_pa}`;

            tr.innerHTML = `
                <td><span class="badge-priority">${r.id}</span></td>
                <td>${timeBadge}</td>
                <td><span class="badge-pa-num" title="${UI.escapeHtml(paTexto)}">PA ${r.num_pa}</span></td>
                <td><span class="badge-matricula">${r.matricula}</span></td>
                <td><strong>${cobradorLabel}</strong></td>
                <td><span class="badge-fila">${UI.escapeHtml(r.fila)}</span></td>
                <td><span class="fone-text">${UI.escapeHtml(r.telefone || '-')}</span></td>
                <td>${statusBadge}</td>
                <td>
                    <div class="row-actions">
                        ${toggleBtn}
                        <button class="btn btn-secondary btn-icon" onclick="appContext.editarItem(${r.id})" title="Editar">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-danger btn-icon" onclick="appContext.confirmarExclusao(${r.id})" title="Excluir">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            `;
            UI.cobrancaTbody.appendChild(tr);
        });

        UI.pageStart.textContent = startIdx;
        UI.pageEnd.textContent = endIdx;
        UI.pageTotal.textContent = totalItems;
        UI.pageCurrentLabel.textContent = `Página ${currentPage} de ${totalPages}`;
        UI.btnPrevPage.disabled = currentPage === 1;
        UI.btnNextPage.disabled = currentPage === totalPages;
    },

    renderizarGraficos: (data) => {
        if (typeof Chart === 'undefined') return;
        const colorsPrimary = ['#003641', '#005c6d', '#9FB100', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899'];
        
        if (window.chartTimesInstance) window.chartTimesInstance.destroy();
        const ctxTimes = document.getElementById('chart-times');
        if (ctxTimes && data.por_time) {
            window.chartTimesInstance = new Chart(ctxTimes, {
                type: 'doughnut',
                data: { labels: data.por_time.map(x => x.label), datasets: [{ data: data.por_time.map(x => x.count), backgroundColor: colorsPrimary }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
        
        if (window.chartPasInstance) window.chartPasInstance.destroy();
        const ctxPas = document.getElementById('chart-pas');
        if (ctxPas && data.por_pa) {
            window.chartPasInstance = new Chart(ctxPas, {
                type: 'bar',
                data: { labels: data.por_pa.map(x => `PA ${x.pa}`), datasets: [{ label: 'Cobradores', data: data.por_pa.map(x => x.count), backgroundColor: '#005c6d' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }

        if (window.chartStatusInstance) window.chartStatusInstance.destroy();
        const ctxStatus = document.getElementById('chart-status');
        if (ctxStatus && data.por_status) {
            const statusMap = { 1: 'Ativos', 0: 'Inativos' };
            window.chartStatusInstance = new Chart(ctxStatus, {
                type: 'pie',
                data: { labels: data.por_status.map(x => statusMap[x.status] || 'Outro'), datasets: [{ data: data.por_status.map(x => x.count), backgroundColor: ['#10b981', '#ef4444'] }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    }
};
