// Configuração inicial
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
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${messageData.is_mine ? 'mine' : 'theirs'}`;
    messageDiv.setAttribute('data-message-id', messageData.id);
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${messageData.content}
        </div>
        <div class="message-time">
            ${messageData.timestamp}
        </div>
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