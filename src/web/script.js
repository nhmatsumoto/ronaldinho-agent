const menuItems = document.querySelectorAll('.menu-item');
const tabPanes = document.querySelectorAll('.tab-pane');
const viewTitle = document.getElementById('view-title');
const saveBtn = document.getElementById('save-all-btn');
const toast = document.getElementById('toast');

const CORE_URL = 'http://localhost:5000';

// Tab switching
menuItems.forEach(item => {
    item.addEventListener('click', () => {
        const target = item.getAttribute('data-tab');
        
        menuItems.forEach(i => i.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));
        
        item.classList.add('active');
        document.getElementById(`tab-${target}`).classList.add('active');
        
        viewTitle.innerText = item.innerText.trim();
    });
});

function showToast(msg) {
    toast.innerText = msg;
    toast.classList.add('active');
    setTimeout(() => toast.classList.remove('active'), 3000);
}

// Stats & Config Fetching
async function syncDashboard() {
    try {
        const [healthRes, configRes] = await Promise.all([
            fetch(`${CORE_URL}/health`),
            fetch(`${CORE_URL}/api/config`)
        ]);

        if (healthRes.ok) {
            const health = await healthRes.json();
            document.getElementById('status-core').innerText = "Online";
            document.getElementById('status-team').innerText = `${health.active_team_count} Especialistas`;
            document.getElementById('val-llm').innerText = health.llm_provider.toUpperCase();
            document.getElementById('val-ghost').innerText = health.browser_ghost_mode === 'active' ? 'Ativo' : 'Logoff';
            document.getElementById('val-telegram').innerText = health.telegram_active ? 'Conectado' : 'Offline';
        }

        if (configRes.ok) {
            const config = await configRes.json();
            document.getElementById('key-gemini').value = config.GEMINI_API_KEY;
            document.getElementById('key-openai').value = config.OPENAI_API_KEY;
            document.getElementById('key-nvidia').value = config.NVIDIA_API_KEY;
            document.getElementById('key-telegram').value = config.TELEGRAM_BOT_TOKEN;
            document.getElementById('model-priority').value = config.MODEL_PRIORITY;
        }
    } catch (e) {
        document.getElementById('status-core').innerText = "Offline";
        document.getElementById('status-core').className = "value";
    }
}

// Save Config
saveBtn.addEventListener('click', async () => {
    const keys = {
        GEMINI_API_KEY: document.getElementById('key-gemini').value,
        OPENAI_API_KEY: document.getElementById('key-openai').value,
        NVIDIA_API_KEY: document.getElementById('key-nvidia').value,
        TELEGRAM_BOT_TOKEN: document.getElementById('key-telegram').value,
        MODEL_PRIORITY: document.getElementById('model-priority').value
    };

    try {
        saveBtn.innerText = "Salvando...";
        saveBtn.disabled = true;

        const res = await fetch(`${CORE_URL}/api/config/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keys })
        });

        if (res.ok) {
            showToast("Configurações salvas! ⚽");
        } else {
            showToast("Erro ao salvar configurações.");
        }
    } catch (e) {
        showToast("Falha técnica de conexão.");
    } finally {
        saveBtn.innerText = "Salvar Alterações";
        saveBtn.disabled = false;
    }
});

// Trigger Browser Login
async function triggerBrowserLogin() {
    try {
        const res = await fetch(`${CORE_URL}/api/browser/login`, {
            method: 'POST'
        });
        if (res.ok) {
            showToast("🚀 Abrindo navegador de login...");
        } else {
            showToast("❌ Falha ao abrir navegador.");
        }
    } catch (e) {
        showToast("Falha de conexão com o Core.");
    }
}

// Initial Sync
syncDashboard();
setInterval(syncDashboard, 15000);
