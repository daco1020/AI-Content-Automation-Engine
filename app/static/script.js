const generateBtn = document.getElementById('generate-btn');
const progressFill = document.getElementById('progress-fill');
const currentStepText = document.getElementById('current-step');
const progressPercentText = document.getElementById('progress-percent');
const logsContainer = document.getElementById('logs');
const videoPlayer = document.getElementById('final-video');
const videoPlaceholderText = document.getElementById('placeholder-text');
const spinner = document.getElementById('spinner');
const globalStatus = document.getElementById('global-status');
const videoActions = document.getElementById('video-actions');
const downloadLink = document.getElementById('download-link');

let statusInterval = null;

async function startGeneration() {
    const language = document.getElementById('lang-select').value;
    const style = document.getElementById('style-input').value;
    const topic = document.getElementById('topic-input').value;
    const quantity = parseInt(document.getElementById('quantity-input').value) || 1;
    const category = document.getElementById('category-select').value;
    const image_source = document.getElementById('image-gen-select').value;

    try {
        const response = await fetch('/api/generate', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language, style, topic, quantity, category, image_source })
        });
        if (response.ok) {
            updateUIForRunning();
            startPolling();
        } else {
            const data = await response.json();
            alert('Error: ' + data.detail);
        }
    } catch (error) {
        console.error('Failed to start generation:', error);
    }
}

function updateUIForRunning() {
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="loading-spinner small"></span> Generando...';
    globalStatus.innerHTML = '<span class="dot pulse"></span> GENERANDO';
    globalStatus.querySelector('.dot').style.background = '#f59e0b';
    globalStatus.querySelector('.dot').style.boxShadow = '0 0 10px #f59e0b';
    spinner.classList.remove('hidden');
    videoPlaceholderText.innerText = 'El motor está trabajando...';
    videoPlayer.classList.add('hidden');
    videoActions.classList.add('hidden');
}

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        // Update progress
        progressFill.style.width = `${status.progress}%`;
        progressPercentText.innerText = `${status.progress}%`;
        currentStepText.innerText = status.current_step;

        // Update logs
        logsContainer.innerHTML = status.log_messages.map(msg => {
            let type = 'system';
            if (msg.includes('✅') || msg.includes('✨')) type = 'success';
            if (msg.includes('❌')) type = 'error';
            return `<div class="log-entry ${type}">${msg}</div>`;
        }).join('');
        logsContainer.scrollTop = logsContainer.scrollHeight;

        // Completion logic
        if (!status.is_running && status.progress === 100) {
            finishGeneration(status.last_video_url);
        } else if (!status.is_running && status.last_error) {
            handleError(status.last_error);
        }
    } catch (error) {
        console.error('Failed to fetch status:', error);
    }
}

function finishGeneration(videoUrl) {
    clearInterval(statusInterval);
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<span class="icon">🚀</span> Iniciar Nueva Generación';
    globalStatus.innerHTML = '<span class="dot"></span> IDLE';
    globalStatus.querySelector('.dot').style.background = '#10b981';
    
    if (videoUrl) {
        // Ensure URL is absolute to the site root
        const fullUrl = videoUrl.startsWith('/') ? videoUrl : '/' + videoUrl;
        
        videoPlayer.src = fullUrl;
        videoPlayer.classList.remove('hidden');
        videoPlaceholderText.classList.add('hidden');
        spinner.classList.add('hidden');
        videoActions.classList.remove('hidden');
        
        // Setup download link
        downloadLink.href = fullUrl;
        const fileName = fullUrl.split('/').pop();
        downloadLink.download = fileName;
        
        // Setup open link
        const openLink = document.getElementById('open-link');
        if (openLink) openLink.href = fullUrl;
    }
}

function handleError(error) {
    clearInterval(statusInterval);
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<span class="icon">🚀</span> Reintentar Generación';
    globalStatus.innerHTML = '<span class="dot error"></span> ERROR';
    globalStatus.querySelector('.dot').style.background = '#f43f5e';
    spinner.classList.add('hidden');
    videoPlaceholderText.innerText = 'Ocurrió un error. Revisa los logs.';
    alert('Error en la generación: ' + error);
}

function startPolling() {
    if (statusInterval) clearInterval(statusInterval);
    statusInterval = setInterval(fetchStatus, 1500);
}

generateBtn.addEventListener('click', startGeneration);

// Initial check
fetchStatus();
if (statusInterval === null) startPolling();
