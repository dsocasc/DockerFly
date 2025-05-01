// Obtenemos referencias a los elementos del DOM
const urlInput = document.getElementById('url');
const submitButton = document.getElementById('submit-button');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');


let serverUrl = '';

async function loadConfig() {
    try {
        if (typeof jsyaml === 'undefined') {
            await loadJsYaml();
        }
        
        const response = await fetch('config.yml');
        if (!response.ok) {
            throw new Error('No se pudo cargar el archivo de configuración');
        }
        
        const configText = await response.text();
        const config = jsyaml.load(configText);
        
        if (config && config.ui && config.ui.server_url) {
            serverUrl = config.ui.server_url;
            console.log('URL del servidor cargada:', serverUrl);
        } else {
            throw new Error('No se encontró la URL del servidor en el archivo de configuración');
        }
    } catch (error) {
        console.error('Error al cargar configuración:', error);
        errorMessage.textContent = 'Error al cargar la configuración: ' + error.message;
        errorMessage.classList.remove('hidden');
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

loadConfig();

submitButton.addEventListener('click', async function() {
    errorMessage.classList.add('hidden');
    successMessage.classList.add('hidden');
    
    const url = urlInput.value.trim();
    
    if (!url) {
        errorMessage.textContent = 'Por favor, introduce una URL válida';
        errorMessage.classList.remove('hidden');
        return;
    }
    
    submitButton.disabled = true;
    submitButton.innerHTML = '<div class="spinner"></div> Procesando...';
    
    try {
        const response = await fetch(`${serverUrl}`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Ha ocurrido un error');
        }
        
        // Mostrar mensaje de éxito
        successMessage.classList.remove('hidden');
        
        // Opcional: Limpiar el campo de entrada
        urlInput.value = '';
        
    } catch (error) {
        // Mostrar mensaje de error
        errorMessage.textContent = error.message || 'Ha ocurrido un error al procesar la solicitud';
        errorMessage.classList.remove('hidden');
    } finally {
        // Restablecer el botón
        submitButton.disabled = false;
        submitButton.innerHTML = 'Enviar';
    }
});

// También permitimos enviar con la tecla Enter
urlInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        submitButton.click();
    }
});