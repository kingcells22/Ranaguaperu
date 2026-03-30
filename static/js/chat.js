const chatToggle = document.getElementById('chat-toggle');
const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const chatContent = document.getElementById('chat-content');

chatToggle.addEventListener('click', () => {
    chatWindow.classList.toggle('hidden');
    chatInput.focus();
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Mensaje del usuario
    chatContent.innerHTML += `
        <div class="flex justify-end">
            <div class="bg-green-600 text-white p-3 rounded-2xl rounded-tr-none shadow-md text-sm max-w-[85%] animate-fade-in">
                ${message}
            </div>
        </div>
    `;
    chatInput.value = '';
    chatContent.scrollTop = chatContent.scrollHeight;

    // Mostrar "Pensando..."
    const loadingId = 'loading-' + Date.now();
    chatContent.innerHTML += `
        <div id="${loadingId}" class="flex gap-2 items-center text-xs text-slate-400 italic py-2">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
            Analizando consulta técnica...
        </div>
    `;
    chatContent.scrollTop = chatContent.scrollHeight;

    // Petición al backend FastAPI
    const formData = new FormData();
    formData.append('message', message);

    try {
        const response = await fetch('/ask', { method: 'POST', body: formData });
        const data = await response.json();
        
        document.getElementById(loadingId).remove();

        // Respuesta de la IA
        chatContent.innerHTML += `
            <div class="flex">
                <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm text-sm border border-slate-100 max-w-[85%] text-slate-700 animate-fade-in">
                    ${data.reply}
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById(loadingId).innerText = "Error de conexión con el servidor.";
    }
    chatContent.scrollTop = chatContent.scrollHeight;
}

chatInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });