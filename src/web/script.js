const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const personaName = document.getElementById('persona-name');
const personaStatus = document.getElementById('persona-status');
const statusModel = document.getElementById('status-model');

const API_URL = 'http://localhost:5000/api/chat';

function addMessage(text, type = 'system') {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}`;
    
    // Simple markdown-to-html (bold only for now)
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');
    
    msgDiv.innerHTML = `<div class="bubble">${formattedText}</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    userInput.value = '';
    addMessage(text, 'user');

    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message system typing';
    typingDiv.innerHTML = '<div class="bubble">...</div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        chatMessages.removeChild(typingDiv);

        if (response.ok) {
            const data = await response.json();
            addMessage(data.response);
            
            // Check if persona changed (heuristic)
            if (text.toLowerCase().includes('arquitetura')) personaName.innerText = "Ronaldinho (Arquiteto)";
            else if (text.toLowerCase().includes('frontend')) personaName.innerText = "Ronaldinho (Frontend)";
            else if (text.toLowerCase().includes('bug')) personaName.innerText = "Ronaldinho (Reviewer)";
            else personaName.innerText = "Ronaldinho (Orquestrador)";

        } else {
            addMessage("❌ Erro ao conectar com o Core.");
        }
    } catch (error) {
        chatMessages.removeChild(typingDiv);
        addMessage("❌ Falha crítica de conexão.");
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-expand textarea
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Fetch initial health
async function checkHealth() {
    try {
        const res = await fetch('http://localhost:5000/health');
        if (res.ok) {
            const data = await res.json();
            statusModel.innerText = data.llm_provider.toUpperCase();
        }
    } catch (e) {}
}

checkHealth();
setInterval(checkHealth, 10000);
