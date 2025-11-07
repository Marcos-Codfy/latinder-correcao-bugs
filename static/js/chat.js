// NOVO BLOCO - Roda quando a página carrega
// Corrige o fuso horário das mensagens já carregadas pelo HTML
document.addEventListener('DOMContentLoaded', function() {
    // Procura todos os elementos de tempo das mensagens já carregadas
    document.querySelectorAll('.message-time[data-timestamp]').forEach(function(timeElement) {
        const isoTimestamp = timeElement.dataset.timestamp;
        if (isoTimestamp) {
            const messageDate = new Date(isoTimestamp);
            const localTime = messageDate.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            // Coloca o horário local formatado dentro do div
            timeElement.textContent = localTime;
        }
    });
});
// --- FIM DO NOVO BLOCO ---


// Configuração inicial (código original)
const messagesArea = document.getElementById('messagesArea');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const matchId = document.getElementById('matchId').value;
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

// ID da última mensagem carregada (para polling)
let lastMessageId = parseInt(messagesArea.dataset.lastMessageId) || 0;

// Função para rolar para o final do chat
function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Rola para o final ao carregar a página
scrollToBottom();

// Função para adicionar uma mensagem na tela
function addMessageToScreen(messageData) {
    
    // <-- MUDANÇA 1: REMOVER MENSAGEM DE "VAZIO" ---
    // Procura pela mensagem "Nenhuma mensagem"
    const emptyMessage = document.getElementById('emptyChatMessage');
    // Se ela existir, remove
    if (emptyMessage) {
        emptyMessage.remove();
    }
    // --- FIM DA MUDANÇA 1 ---


    // <-- MUDANÇA 2: CORREÇÃO DO FUSO HORÁRIO ---
    // Converte o timestamp ISO (que vem do backend) para um objeto Data do JS
    const messageDate = new Date(messageData.timestamp);
    
    // Formata para o horário local do navegador (ex: "13:00")
    const localTime = messageDate.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    // --- FIM DA MUDANÇA 2 ---

    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${messageData.is_mine ? 'mine' : 'theirs'}`;
    messageDiv.setAttribute('data-message-id', messageData.id);
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${messageData.content}
        </div>
        <div class="message-time">
            ${localTime} </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
    
    // Atualiza o ID da última mensagem
    lastMessageId = messageData.id;
}

// Função para enviar mensagem (AJAX)
messageForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const content = messageInput.value.trim();
    if (!content) return;
    
    // Desabilita input durante o envio
    messageInput.disabled = true;
    
    // Envia mensagem para o backend
    fetch('/api/send-message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            match_id: matchId,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Adiciona mensagem na tela
            addMessageToScreen(data.message);
            
            // Limpa o campo de input
            messageInput.value = '';
        } else {
            alert('Erro ao enviar mensagem: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao enviar mensagem');
    })
    .finally(() => {
        // Reabilita input
        messageInput.disabled = false;
        messageInput.focus();
    });
});

// Função para buscar novas mensagens (Polling)
function fetchNewMessages() {
    fetch(`/api/get-messages/?match_id=${matchId}&last_message_id=${lastMessageId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.messages.length > 0) {
                // Adiciona cada mensagem nova na tela
                data.messages.forEach(message => {
                    addMessageToScreen(message);
                });
            }
        })
        .catch(error => {
            console.error('Erro ao buscar mensagens:', error);
        });
}

// Inicia o polling: busca novas mensagens a cada 5 segundos
setInterval(fetchNewMessages, 5000);