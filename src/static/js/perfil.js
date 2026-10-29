document.addEventListener('DOMContentLoaded', () => {
    cargarDatosPerfil();
});

// Carga los datos actuales cuando se abre el perfil
async function cargarDatosPerfil() {
    const username = sessionStorage.getItem('usuario_activo');
    if (!username) return;

    try {
        const resp = await fetch(`/perfil/datos/${username}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            // Llenar campos
            document.getElementById('perfil_username').value = data.username;
            document.getElementById('perfil_nombre').value = data.nombreCompleto;
            document.getElementById('perfil_dni').value = data.dni;
            
            // Campos editables
            document.getElementById('perfil_correo').value = data.correo;
            document.getElementById('perfil_celular').value = data.celular;
            document.getElementById('perfil_direccion').value = data.direccion;
        } else {
            alert("No se pudieron cargar los datos del perfil.");
        }
    } catch (error) {
        console.error("Error al cargar el perfil:", error);
    }
}

// Guarda los cambios
async function guardarPerfil(e) {
    e.preventDefault();
    const username = sessionStorage.getItem('usuario_activo');
    
    const payload = {
        correo: document.getElementById('perfil_correo').value.trim(),
        celular: document.getElementById('perfil_celular').value.trim(),
        direccion: document.getElementById('perfil_direccion').value.trim()
    };

    try {
        const resp = await fetch(`/perfil/${username}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (resp.ok) {
            alert("¡Tu perfil ha sido actualizado correctamente!");
        } else {
            const err = await resp.json();
            // Mostrar error 422 si falla pydantic o 400 personalizado
            if (Array.isArray(err.detail)) {
                alert("Error de validación: " + err.detail[0].msg);
            } else {
                alert(err.detail || "Error al actualizar el perfil.");
            }
        }
    } catch (error) {
        alert("Error de conexión al guardar el perfil.");
    }
}