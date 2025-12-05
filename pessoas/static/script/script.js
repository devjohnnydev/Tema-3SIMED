// ===== VARIÁVEIS GLOBAIS =====
let currentDate = new Date();
let selectedDate = null;
let selectedTimeSlot = null;

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    const calendarContainer = document.getElementById('calendarDays');
    if (calendarContainer) {
        renderCalendar();
        setupEventListeners();
    }
});

// ===== RENDERIZAR CALENDÁRIO =====
function renderCalendar() {
    const calendarDays = document.getElementById('calendarDays');
    if (!calendarDays) return;
    
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Atualizar título do mês
    const monthNames = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    const monthYearElement = document.getElementById('monthYear');
    if (monthYearElement) monthYearElement.textContent = `${monthNames[month]}`;
    
    // Atualizar o título do calendário no topo (Janeiro)
    const calendarHeaderTop = document.querySelector('.calendar-header-top h2');
    if (calendarHeaderTop) calendarHeaderTop.textContent = monthNames[month];
    
    // Limpar dias anteriores
    calendarDays.innerHTML = '';
    
    // Primeiro dia do mês
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const prevLastDay = new Date(year, month, 0);
    
    const firstDayOfWeek = firstDay.getDay();
    const lastDateOfMonth = lastDay.getDate();
    const prevLastDate = prevLastDay.getDate();
    
    // Adicionar dias do mês anterior
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        const dayElement = createDayElement(prevLastDate - i, true);
        calendarDays.appendChild(dayElement);
    }
    
    // Adicionar dias do mês atual
    let firstDayElement = null;
    for (let i = 1; i <= lastDateOfMonth; i++) {
        const dayElement = createDayElement(i, false);
        calendarDays.appendChild(dayElement);
        if (i === 1) {
            firstDayElement = dayElement;
        }
    }
    
    // Adicionar dias do próximo mês
    const totalCells = calendarDays.children.length;
    const remainingCells = 42 - totalCells; // 6 linhas x 7 dias
    for (let i = 1; i <= remainingCells; i++) {
        const dayElement = createDayElement(i, true);
        calendarDays.appendChild(dayElement);
    }

    // Selecionar o primeiro dia do mês por padrão (se não houver seleção)
    if (!selectedDate && firstDayElement) {
        selectDay(firstDayElement, 1);
    }
}

// ===== CRIAR ELEMENTO DO DIA =====
function createDayElement(day, isOtherMonth) {
    const dayElement = document.createElement('div');
    dayElement.className = 'day day-cell';
    dayElement.textContent = day;
    
    if (isOtherMonth) {
        dayElement.classList.add('other-month');
    } else {
        dayElement.addEventListener('click', function() {
            selectDay(this, day);
        });
    }
    
    return dayElement;
}

// ===== SELECIONAR DIA =====
function selectDay(element, day) {
    // Remover seleção anterior
    const previousSelected = document.querySelector('.day.selected');
    if (previousSelected) {
        previousSelected.classList.remove('selected');
    }
    
    // Adicionar seleção ao novo dia
    element.classList.add('selected');
    
    // Atualizar data selecionada
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    selectedDate = new Date(year, month, day);
    
    // Atualizar título da data
    updateDateTitle();
    
    // Resetar seleção de horário
    resetTimeSlotSelection();
}

// ===== ATUALIZAR TÍTULO DA DATA =====
function updateDateTitle() {
    if (!selectedDate) return;
    
    const dayNames = ['Domingo', 'Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado'];
    const monthNames = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    const day = selectedDate.getDate();
    const month = monthNames[selectedDate.getMonth()];
    const dayName = dayNames[selectedDate.getDay()];
    
    document.getElementById('dateTitle').textContent = `${day} de ${month}, ${dayName}`;
}

// ===== RESETAR SELEÇÃO DE HORÁRIO =====
function resetTimeSlotSelection() {
    const allSlots = document.querySelectorAll('.time-slot');
    allSlots.forEach(slot => {
        slot.classList.remove('selected');
    });
    selectedTimeSlot = null;
}

// ===== CONFIGURAR EVENT LISTENERS =====
function setupEventListeners() {
    // Botões de navegação do calendário
    document.querySelector('.prev-btn').addEventListener('click', previousMonth);
    document.querySelector('.next-btn').addEventListener('click', nextMonth);
    
    // Time slots
    const timeSlots = document.querySelectorAll('.time-slot');
    timeSlots.forEach(slot => {
        slot.addEventListener('click', function() {
            selectTimeSlot(this);
        });
    });

    // Botão de confirmação
    document.getElementById('confirmButton').addEventListener('click', confirmAppointment);
}

// ===== MESES ANTERIORES =====
function previousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

// ===== PRÓXIMOS MESES =====
function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

// ===== SELECIONAR HORÁRIO =====
function selectTimeSlot(element) {
    // Remover seleção anterior
    if (selectedTimeSlot) {
        selectedTimeSlot.classList.remove('selected');
    }
    
    // Adicionar seleção ao novo slot
    element.classList.add('selected');
    selectedTimeSlot = element;
    
    // Para fins de demonstração, vamos atribuir um horário ao slot.
    // Em um cenário real, você precisaria calcular o horário baseado na posição do slot na grade.
    // O horário está agora no atributo data-time do próprio slot (ajustado no HTML)
    // No entanto, para garantir que o horário correto seja lido, vamos usar o atributo
    const time = element.getAttribute('data-time');
    
    // Se o horário não estiver no data-time do slot, podemos tentar buscar no cabeçalho
    if (!time) {
        const timeHeaders = document.querySelectorAll('.times-header');
        // O elemento pai é a div.time-slot-row. Os filhos são os slots.
        // O índice do slot dentro da linha corresponde ao índice do cabeçalho de horário.
        const slotIndex = Array.from(element.parentNode.children).indexOf(element);
        const headerTime = timeHeaders[slotIndex] ? timeHeaders[slotIndex].textContent : 'Horário Desconhecido';
        element.setAttribute('data-time', headerTime);
    }
    
    // Log para debug (opcional)
    console.log('Horário selecionado:', selectedTimeSlot);
}

// ===== CONFIRMAR AGENDAMENTO =====
function confirmAppointment() {
    if (!selectedDate) {
        alert('Por favor, selecione um dia no calendário.');
        return;
    }

    if (!selectedTimeSlot) {
        alert('Por favor, selecione um horário na grade de agendamento.');
        return;
    }

    const day = selectedDate.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    const time = selectedTimeSlot.getAttribute('data-time');
    
    // Para obter o nome do profissional/sala, subimos até o pai da linha
    const professionalRow = selectedTimeSlot.closest('.time-slot-row');
    const professionalName = professionalRow ? professionalRow.getAttribute('data-professional') : 'Não Identificado';

    alert(`Agendamento Confirmado!
Dia: ${day}
Horário: ${time}
Profissional/Sala: ${professionalName}`);
}

// Inicio checkup //

// Dados de exemplo para os tratamentos (usados em ambas as páginas)
const treatments = [
    {
        id: 'dental',
        name: 'Check-up Odontológico Completo',
        description: 'Avaliação detalhada da saúde bucal, incluindo análise de cáries, gengivas e oclusão.',
        includes: [
            'Consulta e Avaliação Inicial',
            'Radiografia Panorâmica Digital',
            'Limpeza Profilática (Remoção de Tártaro e Placa)',
            'Aplicação de Flúor',
            'Plano de Tratamento Personalizado'
        ],
        value: 'Variável (a partir de R$ 350,00)'
    },
    {
        id: 'dermato',
        name: 'Rastreio Dermatológico',
        description: 'Exame completo da pele para identificação precoce de lesões suspeitas e avaliação geral da saúde cutânea.',
        includes: [
            'Mapeamento Corporal de Sinais (Dermatoscopia)',
            'Avaliação de Manchas e Lesões',
            'Orientações sobre Cuidados com a Pele e Proteção Solar'
        ],
        value: 'Variável (a partir de R$ 500,00)'
    },
    {
        id: 'nutri',
        name: 'Avaliação Nutricional Completa',
        description: 'Análise de hábitos alimentares e composição corporal para elaboração de um plano nutricional.',
        includes: [
            'Anamnese Detalhada',
            'Avaliação Antropométrica (Peso, Altura, IMC)',
            'Análise da Composição Corporal (Bioimpedância)',
            'Plano Alimentar Personalizado'
        ],
        value: 'Variável (a partir de R$ 280,00)'
    },
    {
        id: 'oftalmo-basico',
        name: 'Tratamento Completo de Oftalmologia Básico',
        description: 'Tratamento oftalmológico básico para cuidados essenciais com a saúde ocular.',
        includes: [
            'Consulta Oftalmológica',
            'Exame de Refração',
            'Medição de Pressão Intraocular',
            'Prescrição de Óculos ou Lentes (se necessário)'
        ],
        value: 'R$ 500,00'
    },
    {
        id: 'cirurgia-basica',
        name: 'Cirurgia Básica',
        description: 'Procedimento cirúrgico de baixa complexidade.',
        includes: [
            'Avaliação Pré-Operatória',
            'Procedimento Cirúrgico',
            'Acompanhamento Pós-Operatório'
        ],
        value: 'R$ 1.000,00'
    },
    {
        id: 'cirurgia-media',
        name: 'Cirurgia Média',
        description: 'Procedimento cirúrgico de média complexidade.',
        includes: [
            'Avaliação Pré-Operatória Completa',
            'Procedimento Cirúrgico',
            'Acompanhamento Pós-Operatório Especializado'
        ],
        value: 'R$ 1.400,00'
    },
    {
        id: 'cirurgia-dificil',
        name: 'Cirurgia Difícil',
        description: 'Procedimento cirúrgico de alta complexidade.',
        includes: [
            'Avaliação Pré-Operatória Detalhada',
            'Procedimento Cirúrgico Complexo',
            'Acompanhamento Pós-Operatório Intensivo'
        ],
        value: 'R$ 2.000,00'
    },
    {
        id: 'exames-gerais',
        name: 'Exames Gerais',
        description: 'Conjunto de exames laboratoriais e clínicos básicos.',
        includes: [
            'Hemograma Completo',
            'Glicemia',
            'Colesterol Total e Frações',
            'Exame de Urina'
        ],
        value: 'R$ 300,00'
    },
    {
        id: 'exames-especificos',
        name: 'Exames Específicos',
        description: 'Exames laboratoriais e de imagem especializados.',
        includes: [
            'Exames Específicos Conforme Solicitação Médica',
            'Análises Laboratoriais Especializadas',
            'Laudos Detalhados'
        ],
        value: 'R$ 500,00'
    },
    {
        id: 'consulta-geral',
        name: 'Consulta Geral',
        description: 'Consulta médica geral para avaliação de saúde.',
        includes: [
            'Anamnese Completa',
            'Exame Físico',
            'Orientações e Prescrições Médicas'
        ],
        value: 'R$ 300,00'
    },
    {
        id: 'odonto-basico',
        name: 'Tratamento Completo de Odontologia Básico',
        description: 'Tratamento odontológico básico para manutenção da saúde bucal.',
        includes: [
            'Consulta Odontológica',
            'Limpeza e Profilaxia',
            'Aplicação de Flúor',
            'Orientações de Higiene Bucal'
        ],
        value: 'R$ 500,00'
    },
    {
        id: 'tomografia',
        name: 'Tomografia',
        description: 'Exame de imagem por tomografia computadorizada.',
        includes: [
            'Tomografia Computadorizada',
            'Laudo Médico Especializado',
            'Imagens Digitais'
        ],
        value: 'R$ 300,00'
    }
];

document.addEventListener('DOMContentLoaded', () => {
    // --- Lógica para checkup_cliente.html (Página Inicial) ---
    const checkupInput = document.getElementById('checkup-input');
    const selectionList = document.getElementById('checkup-selection-list');

    if (checkupInput && selectionList) {
        treatments.forEach(treatment => {
            const item = document.createElement('div');
            item.classList.add('selection-list-item');
            item.textContent = treatment.name;
            item.dataset.id = treatment.id;
            selectionList.appendChild(item);
        });

        checkupInput.addEventListener('focus', () => {
            selectionList.style.display = 'block';
        });

        document.addEventListener('click', (event) => {
            if (!checkupInput.contains(event.target) && !selectionList.contains(event.target)) {
                selectionList.style.display = 'none';
            }
        });

        selectionList.addEventListener('click', (event) => {
            const item = event.target.closest('.selection-list-item');
            if (item) {
                const selectedName = item.textContent;
                const selectedId = item.dataset.id;
                checkupInput.value = selectedName;
                selectionList.style.display = 'none';
                window.location.href = CHECKUP_TRATAMENTO_URL + '?checkupId=' + selectedId;
            }
        });
    }

    // --- Lógica para checkup_cliente_pos.html (Página Pós-Busca) ---
    const selectElement = document.getElementById('treatment-select');
    const detailsContainer = document.getElementById('treatment-details-container');
    const checkupInputPos = document.getElementById('checkup-input-pos');

    // Função para exibir os detalhes do tratamento (usada na página pós-busca)
    function displayTreatmentDetails(id) {
        console.log('Tentando exibir detalhes para o ID:', id);
        if (!detailsContainer) {
            console.error('ERRO: O contêiner de detalhes (#treatment-details-container) não foi encontrado.');
            return;
        }

        detailsContainer.innerHTML = ''; // Limpa o conteúdo anterior

        if (!id) {
            detailsContainer.style.display = 'none';
            console.log('Nenhum ID selecionado, detalhes ocultos.');
            return;
        }

        const treatment = treatments.find(t => t.id === id);

        if (treatment) {
            console.log('Tratamento encontrado:', treatment.name);
            const includesList = treatment.includes.map(item => `<li>${item}</li>`).join('');

            const htmlContent = `
                <div class="treatment-details">
                    <h3>${treatment.name}</h3>
                    <p>${treatment.description}</p>
                    <h4>O que inclui:</h4>
                    <ul>${includesList}</ul>
                    <div class="value-box">
                        <span class="real-value">Valor Estimado: ${treatment.value}</span>
                    </div>
                    <button class="btn-print" onclick="window.print()">Imprimir Detalhes</button>
                </div>
            `;

            detailsContainer.innerHTML = htmlContent;
            detailsContainer.style.display = 'flex';
            console.log('Detalhes exibidos com sucesso.');
        } else {
            detailsContainer.style.display = 'none';
            console.log('Nenhum tratamento encontrado para o ID:', id);
        }
    }

    if (selectElement) {
        console.log('Página Pós-Busca detectada. Inicializando lógica...');
        
        // 1. Popular o dropdown
        treatments.forEach(treatment => {
            const option = document.createElement('option');
            option.value = treatment.id;
            option.textContent = treatment.name;
            selectElement.appendChild(option);
        });

        // 2. Ouvir a mudança no dropdown
        selectElement.addEventListener('change', (event) => {
            const selectedId = event.target.value;
            console.log('Dropdown alterado. ID selecionado:', selectedId);
            displayTreatmentDetails(selectedId);
        });

        // 3. Carregar o check-up selecionado via URL
        const urlParams = new URLSearchParams(window.location.search);
        const selectedCheckupId = urlParams.get('checkupId');

        if (selectedCheckupId) {
            console.log('ID de check-up encontrado na URL:', selectedCheckupId);
            const selectedCheckup = treatments.find(t => t.id === selectedCheckupId);
            if (selectedCheckup) {
                if (checkupInputPos) {
                    checkupInputPos.value = selectedCheckup.name;
                }
                // Pré-seleciona o item no dropdown
                selectElement.value = selectedCheckupId;
                // E exibe os detalhes imediatamente
                displayTreatmentDetails(selectedCheckupId);
            }
        }
    }
});

// Fim checkup //