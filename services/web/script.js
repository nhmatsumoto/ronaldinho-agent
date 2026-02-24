const API_URL = 'http://localhost:5000';
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const coreStatus = document.getElementById('core-status');
const authStatus = document.getElementById('auth-status');

// Verificação de saúde do Core
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        if (data.status === 'ok') {
            coreStatus.innerHTML = '<span class="status-dot"></span> Core Online';
            coreStatus.classList.add('online');
        }
    } catch (error) {
        console.error('Core offline:', error);
        coreStatus.innerHTML = '<span class="status-dot"></span> Core Offline';
        coreStatus.classList.remove('online');
    }
}

// OAuth2 Logic
async function startOAuth(provider) {
    try {
        const response = await fetch(`${API_URL}/api/auth/login/${provider}`);
        const data = await response.json();
        if (data.url) {
            window.location.href = data.url;
        } else {
            alert('Erro ao iniciar login: ' + (data.detail || 'Desconhecido'));
        }
    } catch (error) {
        console.error('Auth error:', error);
        alert('Erro de conexão ao iniciar login.');
    }
}

async function updateAuthStatus() {
    try {
        const response = await fetch(`${API_URL}/api/auth/status`);
        const data = await response.json();
        if (data.providers && data.providers.length > 0) {
            authStatus.innerText = 'Conectado: ' + data.providers.join(', ');
        } else {
            authStatus.innerText = 'Nenhum provedor conectado (usando .env)';
        }
    } catch (error) {
        authStatus.innerText = 'Status de conexão indisponível.';
    }
}

// Handle OAuth callback if URL has code
async function handleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    // For simplicity, we assume 'provider' is passed back or we default to google
    if (code) {
        authStatus.innerText = 'Finalizando conexão...';
        try {
            const response = await fetch(`${API_URL}/api/auth/callback?code=${code}`);
            const data = await response.json();
            if (response.ok) {
                appendMessage(`✅ Ronaldinho: ${data.message}`, 'ai');
                // Clean URL
                window.history.replaceState({}, document.title, window.location.pathname);
            } else {
                appendMessage(`❌ Falha na conexão: ${data.detail}`, 'ai');
            }
        } catch (error) {
            console.error('Callback error:', error);
        }
        updateAuthStatus();
    }
}

function appendMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    messageDiv.innerHTML = `<p>${text}</p>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';
    
    // Mostra indicador de digitação (simples)
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'ai', 'typing');
    typingDiv.innerHTML = '<p>Digitando...</p>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, user_id: 'web_user', platform: 'web' })
        });

        const data = await response.json();
        chatMessages.removeChild(typingDiv);
        
        if (!response.ok) {
            appendMessage(`⚠️ Erro: ${data.detail || 'Ocorreu um erro no servidor'}`, 'ai');
            return;
        }

        appendMessage(data.response, 'ai');
    } catch (error) {
        if (chatMessages.contains(typingDiv)) chatMessages.removeChild(typingDiv);
        appendMessage('❌ Desculpe, craque. Erro de conexão com o Core.', 'ai');
        console.error('Error:', error);
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Inicialização
checkHealth();
updateAuthStatus();
handleCallback();
setInterval(checkHealth, 5000);
setInterval(updateAuthStatus, 10000);
