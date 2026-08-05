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
    
    // Stats elements
    statTotal: document.getElementById('stat-total'),
    statTimes: document.getElementById('stat-times'),
    statPas: document.getElementById('stat-pas'),
    statFilas: document.getElementById('stat-filas'),

    // Modais e Barra em Lote
    syncResultModal: document.getElementById('sync-result-modal'),
    syncResultBody: document.getElementById('sync-result-body'),
    bulkActionsBar: document.getElementById('bulk-actions-bar'),
    bulkSelectedCount: document.getElementById('bulk-selected-count'),

    showToast: (message, type = 'info') => {
        if (!UI.toast) return;
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

    renderizarEstatisticas: (totalItems, timesCount, pasCount, filasCount, filasSemCobradorCount, substituicoesAtivasCount = 0) => {
        if (UI.statTotal) UI.statTotal.textContent = totalItems;
        if (UI.statTimes) UI.statTimes.textContent = timesCount;
        if (UI.statPas)   UI.statPas.textContent   = pasCount;
        if (UI.statFilas) UI.statFilas.textContent = filasCount;
        const elSemCob = document.getElementById('stat-filas-sem-cobrador');
        if (elSemCob) elSemCob.textContent = filasSemCobradorCount;
        const elSubAtivas = document.getElementById('stat-substituicoes');
        if (elSubAtivas) elSubAtivas.textContent = substituicoesAtivasCount;
    },

    formatarDataBR: (strDate) => {
        if (!strDate) return '-';
        const parts = strDate.split('-');
        if (parts.length === 3) {
            return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
        return strDate;
    },

    renderizarFilasSemCobrador: (filas, callbackAdicionar) => {
        const tbody = document.getElementById('filas-sem-cob-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        if (!filas || filas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="2" style="text-align:center; padding: 12px; color: #64748b;">Nenhuma fila sem cobrador identificada.</td></tr>`;
            return;
        }
        filas.forEach(item => {
            const nomeFila = typeof item === 'string' ? item : item.fila;
            const numPA = typeof item === 'object' && item.num_pa ? item.num_pa : 0;

            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #e2e8f0';
            
            const tdFila = document.createElement('td');
            tdFila.style.padding = '8px';
            const paBadge = numPA ? `<span class="badge-pa-num" style="margin-left:8px;">PA ${numPA}</span>` : '';
            tdFila.innerHTML = `<strong>${UI.escapeHtml(nomeFila)}</strong>${paBadge}`;
            
            const tdAcao = document.createElement('td');
            tdAcao.style.padding = '8px';
            tdAcao.style.textAlign = 'right';
            
            const btn = document.createElement('button');
            btn.className = 'btn btn-success btn-sm';
            btn.innerHTML = `<i class="fa-solid fa-plus"></i> Adicionar Cobrador`;
            btn.addEventListener('click', () => callbackAdicionar(nomeFila, numPA));
            
            tdAcao.appendChild(btn);
            tr.appendChild(tdFila);
            tr.appendChild(tdAcao);
            tbody.appendChild(tr);
        });
    },

    renderizarTabela: (registros, totalItems, currentPage, totalPages, itemsPerPage, startIdx, endIdx, listaPAs, selectedIds = new Set()) => {
        if (!UI.cobrancaTbody) return;

        if (!registros || registros.length === 0) {
            UI.cobrancaTbody.innerHTML = `<tr><td colspan="13" class="empty-state">
                <i class="fa-solid fa-folder-open"></i><br>Nenhum cobrador encontrado.</td></tr>`;
            if (UI.pageStart) UI.pageStart.textContent = '0';
            if (UI.pageEnd) UI.pageEnd.textContent = '0';
            if (UI.pageTotal) UI.pageTotal.textContent = '0';
            if (UI.pageCurrentLabel) UI.pageCurrentLabel.textContent = 'Página 0 de 0';
            if (UI.btnPrevPage) UI.btnPrevPage.disabled = true;
            if (UI.btnNextPage) UI.btnNextPage.disabled = true;
            UI.atualizarBarraLote(0);
            return;
        }

        UI.cobrancaTbody.innerHTML = '';
        registros.forEach(r => {
            const tr = document.createElement('tr');
            const isAtivo = r.status !== 0 && r.status !== '0';
            if (!isAtivo) tr.classList.add('row-inactive');

            const isChecked = selectedIds.has(r.id) ? 'checked' : '';

            const statusBadge = isAtivo
                ? '<span class="badge-status-active"><i class="fa-solid fa-circle-check"></i> Ativo</span>'
                : '<span class="badge-status-inactive"><i class="fa-solid fa-circle-xmark"></i> Inativo</span>';

            const toggleBtn = isAtivo
                ? `<button class="btn btn-secondary btn-icon" data-action="toggle-status" data-id="${r.id}" data-target-status="0" title="Inativar">
                        <i class="fa-solid fa-toggle-on" style="color: #10b981; font-size: 16px;"></i></button>`
                : `<button class="btn btn-secondary btn-icon" data-action="toggle-status" data-id="${r.id}" data-target-status="1" title="Ativar">
                        <i class="fa-solid fa-toggle-off" style="color: #94a3b8; font-size: 16px;"></i></button>`;

            const timeStr = r.times_cobranca ? String(r.times_cobranca) : '';
            const timeBadge = (timeStr.trim() !== '') ? `<span class="badge-time">${UI.escapeHtml(timeStr)}</span>` : `<span class="badge-time-empty">—</span>`;
            
            let cobradorLabel = UI.escapeHtml(r.cobrador);

            // Renderiza Informações de Substituição (DE-PARA)
            let celulaSubstituto = '<span style="color:#94a3b8;">—</span>';
            let celulaDataInicio = '<span style="color:#94a3b8;">—</span>';
            let celulaDataFim = '<span style="color:#94a3b8;">—</span>';
            let cancelSubBtn = '';

            if (r.substituicao_id) {
                const subNome = UI.escapeHtml(r.substituto_nome || 'Indefinido');
                const dtIni = UI.formatarDataBR(r.data_inicio_substituicao);
                const dtFim = UI.formatarDataBR(r.data_fim_substituicao);
                const isFuturo = r.status_substituicao === 'AGENDADA';

                if (r.papel_substituicao === 'ORIGINAL') {
                    cobradorLabel += ` <span style="font-size:10px; padding:2px 6px; border-radius:4px; font-weight:600; background:#fef08a; color:#854d0e; white-space:nowrap;" title="Cobrador Ausente (Em Férias/Licença)"><i class="fa-solid fa-plane-departure"></i> Ausente</span>`;
                    celulaSubstituto = `<span style="font-size:11px; padding:3px 8px; border-radius:4px; font-weight:600; ${isFuturo ? 'background:#e0f2fe; color:#0369a1;' : 'background:#dcfce7; color:#15803d;'}">
                        <i class="fa-solid ${isFuturo ? 'fa-calendar-clock' : 'fa-user-check'}"></i> <strong>${subNome}</strong> (${isFuturo ? 'Agendado' : 'Substituto'})
                    </span>`;
                } else {
                    cobradorLabel += ` <span style="font-size:10px; padding:2px 6px; border-radius:4px; font-weight:600; background:#f3e8ff; color:#6b21a8; white-space:nowrap;" title="Cobrador em Cobertura Temporária"><i class="fa-solid fa-user-clock"></i> Cobertura</span>`;
                    celulaSubstituto = `<span style="font-size:11px; padding:3px 8px; border-radius:4px; font-weight:600; background:#f3e8ff; color:#6b21a8;">
                        <i class="fa-solid fa-arrows-rotate"></i> Cobrindo <strong>${subNome}</strong>
                    </span>`;
                }

                celulaDataInicio = `<span style="font-size:12px; font-weight:500;">${dtIni}</span>`;
                celulaDataFim = `<span style="font-size:12px; font-weight:500;">${dtFim}</span>`;

                cancelSubBtn = `<button class="btn btn-secondary btn-icon" data-action="cancelar-substituicao" data-sub-id="${r.substituicao_id}" title="Cancelar Substituição" style="color:#ef4444; border-color:#fca5a5;">
                    <i class="fa-solid fa-user-xmark"></i>
                </button>`;
            }

            const paObj = listaPAs.find(x => x.num_pa === r.num_pa);
            const paTexto = paObj ? `PA ${r.num_pa} - ${paObj.nome_pa}` : `PA ${r.num_pa}`;

            tr.innerHTML = `
                <td style="text-align:center;">
                    <input type="checkbox" class="row-checkbox" data-id="${r.id}" ${isChecked}>
                </td>
                <td><span class="badge-priority">${r.id}</span></td>
                <td>${timeBadge}</td>
                <td><span class="badge-pa-num" title="${UI.escapeHtml(paTexto)}">PA ${r.num_pa}</span></td>
                <td><span class="badge-matricula">${r.matricula}</span></td>
                <td><strong>${cobradorLabel}</strong></td>
                <td><span class="badge-fila">${UI.escapeHtml(r.fila)}</span></td>
                <td>${celulaSubstituto}</td>
                <td>${celulaDataInicio}</td>
                <td>${celulaDataFim}</td>
                <td><span class="fone-text">${UI.escapeHtml(r.telefone || '-')}</span></td>
                <td>${statusBadge}</td>
                <td>
                    <div class="row-actions">
                        ${cancelSubBtn}
                        <button class="btn btn-secondary btn-icon" data-action="substituir-linha" data-id="${r.id}" data-cobrador="${UI.escapeHtml(r.cobrador)}" data-matricula="${r.matricula}" title="Substituir Cobrador (Todas as filas)">
                            <i class="fa-solid fa-user-plus" style="color:var(--accent-color);"></i>
                        </button>
                        ${toggleBtn}
                        <button class="btn btn-secondary btn-icon" data-action="edit" data-id="${r.id}" title="Editar">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn btn-danger btn-icon" data-action="delete" data-id="${r.id}" title="Excluir">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            `;
            UI.cobrancaTbody.appendChild(tr);
        });

        if (UI.pageStart) UI.pageStart.textContent = startIdx;
        if (UI.pageEnd) UI.pageEnd.textContent = endIdx;
        if (UI.pageTotal) UI.pageTotal.textContent = totalItems;
        if (UI.pageCurrentLabel) UI.pageCurrentLabel.textContent = `Página ${currentPage} de ${totalPages}`;
        if (UI.btnPrevPage) UI.btnPrevPage.disabled = currentPage === 1;
        if (UI.btnNextPage) UI.btnNextPage.disabled = currentPage === totalPages;

        UI.atualizarBarraLote(selectedIds.size);
    },

    atualizarBarraLote: (count) => {
        if (!UI.bulkActionsBar) return;
        if (count > 0) {
            UI.bulkActionsBar.style.display = 'flex';
            if (UI.bulkSelectedCount) UI.bulkSelectedCount.innerHTML = `<strong>${count}</strong> item(ns) selecionado(s)`;
        } else {
            UI.bulkActionsBar.style.display = 'none';
        }
    },

    renderizarMultiPASuggestions: (listaPAs) => {
        const grid = document.getElementById('item-pas-grid');
        if (!grid) return;
        grid.innerHTML = '';

        listaPAs.forEach(pa => {
            const label = document.createElement('label');
            label.className = 'multi-pa-item';
            const paSearchText = `pa ${pa.num_pa} ${pa.nome_pa || ''}`.toLowerCase();
            label.setAttribute('data-pa-text', paSearchText);
            label.innerHTML = `
                <input type="checkbox" class="item-pa-checkbox" value="${pa.num_pa}">
                <span>PA ${pa.num_pa} - ${UI.escapeHtml(pa.nome_pa || '')}</span>
            `;
            grid.appendChild(label);
        });
    },

    renderizarAuditoria: (auditoriaData) => {
        const tbody = document.getElementById('auditoria-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!auditoriaData || auditoriaData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:12px; color:#64748b;">Nenhum registro de auditoria.</td></tr>`;
            return;
        }

        auditoriaData.forEach(a => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #e2e8f0';
            tr.style.fontSize = '12px';

            const dt = a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : '-';

            let badgeStyle = 'background:#e2e8f0; color:#334155;';
            let acaoTxt = a.tipo_acao || 'AÇÃO';

            if (acaoTxt.includes('CRIACAO')) {
                badgeStyle = 'background:#dcfce7; color:#15803d;';
            } else if (acaoTxt.includes('EXCLUSAO') || acaoTxt.includes('CANCELAMENTO')) {
                badgeStyle = 'background:#fee2e2; color:#b91c1c;';
            } else if (acaoTxt.includes('SUBSTITUICAO') || acaoTxt.includes('TROCA')) {
                badgeStyle = 'background:#dbeafe; color:#1d4ed8;';
            } else if (acaoTxt.includes('STATUS')) {
                badgeStyle = 'background:#fef3c7; color:#b45309;';
            }

            tr.innerHTML = `
                <td style="padding:8px; color:#64748b; font-size:11px;">${dt}</td>
                <td style="padding:8px;"><span class="badge-time" style="${badgeStyle} font-size:10px;">${UI.escapeHtml(acaoTxt)}</span></td>
                <td style="padding:8px;">${UI.escapeHtml(a.cobrador_origem || '-')}</td>
                <td style="padding:8px;"><strong>${UI.escapeHtml(a.cobrador_destino || '-')}</strong></td>
                <td style="padding:8px; text-align:center;">${a.total_afetados}</td>
                <td style="padding:8px; color:#334155;">${UI.escapeHtml(a.detalhe)}</td>
            `;
            tbody.appendChild(tr);
        });
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
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                padding: 6,
                                font: { size: 10 }
                            }
                        }
                    },
                    layout: {
                        padding: { top: 4, bottom: 4 }
                    }
                }
            });
        }
        
        if (window.chartPasInstance) window.chartPasInstance.destroy();
        const ctxPas = document.getElementById('chart-pas');
        if (ctxPas && data.por_pa) {
            window.chartPasInstance = new Chart(ctxPas, {
                type: 'bar',
                data: { labels: data.por_pa.map(x => `PA ${x.pa}`), datasets: [{ label: 'Cobradores', data: data.por_pa.map(x => x.count), backgroundColor: '#005c6d' }] },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            ticks: {
                                precision: 0,
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }

        if (window.chartStatusInstance) window.chartStatusInstance.destroy();
        const ctxStatus = document.getElementById('chart-status');
        if (ctxStatus && data.por_status) {
            const statusMap = { 1: 'Ativos', 0: 'Inativos' };
            window.chartStatusInstance = new Chart(ctxStatus, {
                type: 'pie',
                data: { labels: data.por_status.map(x => statusMap[x.status] || 'Outro'), datasets: [{ data: data.por_status.map(x => x.count), backgroundColor: ['#10b981', '#ef4444'] }] },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                padding: 6,
                                font: { size: 10 }
                            }
                        }
                    },
                    layout: {
                        padding: { top: 4, bottom: 4 }
                    }
                }
            });
        }
    },

    renderizarEscalaSubstituicoes: (escalaData, filtroStatus = 'TODAS') => {
        const tbody = document.getElementById('escala-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!escalaData || escalaData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px; color:#64748b;">Nenhuma substituição registrada na escala.</td></tr>`;
            return;
        }

        const filtradas = escalaData.filter(item => {
            if (!filtroStatus || filtroStatus === 'TODAS') return true;
            return item.status_substituicao === filtroStatus;
        });

        if (filtradas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:16px; color:#64748b;">Nenhuma substituição encontrada com status "${filtroStatus}".</td></tr>`;
            return;
        }

        filtradas.forEach(item => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #e2e8f0';
            tr.style.fontSize = '12px';

            const st = item.status_substituicao || 'AGENDADA';
            let badgeStyle = 'background:#e2e8f0; color:#334155;';
            let icon = 'fa-clock';
            let stText = st;

            if (st === 'EM_ANDAMENTO') {
                badgeStyle = 'background:#dcfce7; color:#15803d;';
                icon = 'fa-user-check';
                stText = 'Em Andamento';
            } else if (st === 'AGENDADA') {
                badgeStyle = 'background:#e0f2fe; color:#0369a1;';
                icon = 'fa-calendar';
                stText = 'Agendada';
            } else if (st === 'CONCLUIDA') {
                badgeStyle = 'background:#f1f5f9; color:#475569;';
                icon = 'fa-check-double';
                stText = 'Concluída';
            } else if (st === 'CANCELADA') {
                badgeStyle = 'background:#fee2e2; color:#b91c1c;';
                icon = 'fa-xmark';
                stText = 'Cancelada';
            }

            const dtIni = UI.formatarDataBR(item.data_inicio);
            const dtFim = UI.formatarDataBR(item.data_fim);

            const origInfo = `<strong>${UI.escapeHtml(item.original_nome)}</strong> <span style="color:#64748b; font-size:11px;">(Mat: ${item.original_matricula} | PA ${item.original_pa} | ${UI.escapeHtml(item.original_fila)})</span>`;
            const subInfo = `<strong>${UI.escapeHtml(item.substituto_nome)}</strong> <span style="color:#64748b; font-size:11px;">(Mat: ${item.substituto_matricula})</span>`;

            let acoes = '<span style="color:#94a3b8;">—</span>';
            if (st === 'AGENDADA' || st === 'EM_ANDAMENTO') {
                acoes = `<button class="btn btn-secondary btn-sm" data-action="cancelar-substituicao-escala" data-sub-id="${item.id}" style="color:#ef4444; border-color:#fca5a5; padding:2px 8px; font-size:11px;" title="Cancelar Substituição">
                    <i class="fa-solid fa-user-xmark"></i> Cancelar
                </button>`;
            }

            tr.innerHTML = `
                <td style="padding:10px;"><span style="display:inline-flex; align-items:center; gap:4px; padding:3px 8px; border-radius:4px; font-weight:600; font-size:11px; ${badgeStyle}"><i class="fa-solid ${icon}"></i> ${stText}</span></td>
                <td style="padding:10px;">${origInfo}</td>
                <td style="padding:10px;">${subInfo}</td>
                <td style="padding:10px;"><strong style="color:#0f172a;">${dtIni}</strong> até <strong style="color:#0f172a;">${dtFim}</strong></td>
                <td style="padding:10px; text-align:center;">${acoes}</td>
            `;
            tbody.appendChild(tr);
        });
    }
};
