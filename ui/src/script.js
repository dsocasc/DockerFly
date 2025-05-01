// Obtenemos referencias a los elementos del DOM
const urlInput = document.getElementById('url');
const submitButton = document.getElementById('submit-button');
const errorMessage = document.getElementById('error-message');
const successMessage = document.getElementById('success-message');

// Función para manejar el envío del formulario
submitButton.addEventListener('click', async function() {
    // Ocultar mensajes anteriores
    errorMessage.classList.add('hidden');
    successMessage.classList.add('hidden');
    
    const url = urlInput.value.trim();
    
    // Validación básica
    if (!url) {
        errorMessage.textContent = 'Por favor, introduce una URL válida';
        errorMessage.classList.remove('hidden');
        return;
    }
    
    // Mostrar indicador de carga
    submitButton.disabled = true;
    submitButton.innerHTML = '<div class="spinner"></div> Procesando...';
    
    try {
        // Hacer la petición al servidor
        const response = await fetch(`http://dockerfly-server.nimbus.net/repo`, {
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