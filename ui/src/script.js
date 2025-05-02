// Obtenemos referencias a los elementos del DOM
const urlInput = document.getElementById('url');
const submitButton = document.getElementById('submit-button');
const errorMessageDiv = document.getElementById('error-message');
const successMessageDiv = document.getElementById('success-message');
const successAppName = document.getElementById('success-app-name');
const successAccessUrl = document.getElementById('success-access-url');
const successContainerId = document.getElementById('success-container-id');
const successCommitHash = document.getElementById('success-commit-hash');

let serverUrl = '';

async function loadConfig() {
    try {
        if (typeof jsyaml === 'undefined') {
            await loadJsYaml();
        }
        
        const response = await fetch('config.yml');
        if (!response.ok) {
            throw new Error(`No se pudo cargar config.yml (status: ${response.status})`);
        }
        
        const configText = await response.text();
        const config = jsyaml.load(configText);
        
        if (config && config.ui && config.ui.server_url) {
            serverUrl = config.ui.server_url;
            console.log('URL del servidor cargada:', serverUrl);

            // Asegurar que la URL base no termine en / para evitar doble // al añadir /repo
            if (serverUrl.endsWith('/')) {
                serverUrl = serverUrl.slice(0, -1);
            }
        } else {
            throw new Error('No se encontró ui.server_url en config.yml');
        }
    } catch (error) {
        console.error('Error al cargar configuración:', error);
        errorMessageDiv.textContent = 'Error al cargar la configuración UI: ' + error.message;
        errorMessageDiv.classList.remove('hidden');
        submitButton.disabled = true;
    }
}

async function loadJsYaml() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js';
        script.onload = resolve;
        script.onerror = () => reject(new Error('No se pudo cargar js-yaml'));
        document.head.appendChild(script);
    });
}

submitButton.addEventListener('click', async function() {
    errorMessageDiv.classList.add('hidden');
    successMessageDiv.classList.add('hidden');
    
    const url = urlInput.value.trim();
    
    if (!url) {
        errorMessageDiv.textContent = 'Por favor, introduce una URL de repositorio Git válida.';
        errorMessageDiv.classList.remove('hidden');
        return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('git@')) {
        errorMessageDiv.textContent = 'La URL debe empezar con http://, https:// o git@';
        errorMessageDiv.classList.remove('hidden');
        return;
    }
    
    submitButton.disabled = true;
    submitButton.innerHTML = '<div class="spinner"></div> Desplegando...';
    
    try {
        const response = await fetch(`${serverUrl}`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            console.error('Error al parsear la respuesta JSON:', jsonError);
            const responseText = await response.text();
            throw new Error(`Error ${response.status}: ${response.statusText}. Response: ${responseText || '(empty)'}`);
        }
        
        if (response.ok) {
            if (successAppName) successAppName.textContent = data.app_name || 'N/D';
            if (successAccessUrl) {
                successAccessUrl.href = data.access_url || '#';
                successAccessUrl.textContent = data.access_url || 'N/D';
                if (!data.access_url) {
                    successAccessUrl.removeAttribute('href');
                    successAccessUrl.style.textDecoration = 'none';
                    successAccessUrl.style.cursor = 'default';
                } else {
                    successAccessUrl.style.textDecoration = '';
                    successAccessUrl.style.cursor = '';
                }
            }
            if (successContainerId) successContainerId.textContent = data.container_id || 'N/D';
            if (successCommitHash) successCommitHash.textContent = data.current_commit ? data.current_commit.substring(0, 7) : 'N/D';

            successMessageDiv.classList.remove('hidden');
            urlInput.value = '';
        } else {
            // Intentar obtener mensaje de error de FastAPI o genérico
            const errorMsg = data?.detail || data?.message || `Error ${response.status}: ${JSON.stringify(data)}`;
            throw new Error(errorMsg);
        }
    } catch (error) {
        // Mostrar mensaje de error
        
        console.error('El despliegue falló:', error);
        errorMessageDiv.textContent = error.message || 'Ha ocurrido un error al procesar la solicitud';
        errorMessageDiv.classList.remove('hidden');
    } finally {
        // Restablecer el botón
        submitButton.disabled = false;
        submitButton.innerHTML = 'Enviar';
    }
});

// También permitimos enviar con la tecla Enter
urlInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        submitButton.click();
    }
});

// Carga de configuración
loadConfig();