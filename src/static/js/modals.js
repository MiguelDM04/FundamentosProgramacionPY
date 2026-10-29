
// Mostrar/Abrir modal
function abrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) modal.style.display = 'flex';
}

// Ocultar/cerrar modal
function cerrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) modal.style.display = 'none';
}

// Cierra modal al hacer clic en donde no hay nada
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// >>> modal nuevo expediente <<<
function ModalNuevoExpediente() {
    const rol = sessionStorage.getItem('rol_activo');
    const campoAdmin = document.getElementById('campo-admin-cliente');
    
    if (rol === 'admin' && campoAdmin) {
        campoAdmin.style.display = 'block';//en caso sea admin muestra el txt para ingresar usuario
    } else if (campoAdmin) {
        campoAdmin.style.display = 'none';
    }
    abrirModal('modal-nuevo-expediente');
}

// >>> modal actualizar expediente <<<
//Carga los datos del expediente en el modal de actualizacion
async function prepararEdicion(codigo) {
    try {
        const resp = await fetch(`/expedientes/${codigo}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            document.getElementById('edit_codigo').value = data.codigo;
            document.getElementById('edit_progreso').value = data.progreso;
            document.getElementById('edit_tramite').value = data.tramite;
            document.getElementById('edit_asunto').value = data.asunto;
            document.getElementById('edit_descripcion').value = data.descripcion;
            document.getElementById('edit_correo').value = data.correo;
            document.getElementById('edit_celular').value = data.celular;
            document.getElementById('edit_direccion').value = data.direccion;

            abrirModal('modal-editar');
        } else {
            alert("No se pudieron cargar los datos del expediente.");
        }
    } catch (error) {
        alert("Error de conexión.");
    }
}
//Guarda los cambios de los datos 
async function procesarEdicion(e) {
    e.preventDefault();//evita que el navegador se recargue auto
    const codigo = document.getElementById('edit_codigo').value;

    const payload = {
        correo: document.getElementById('edit_correo').value.trim(),
        celular: document.getElementById('edit_celular').value.trim(),
        direccion: document.getElementById('edit_direccion').value.trim(),
        tramite: document.getElementById('edit_tramite').value.trim(),
        asunto: document.getElementById('edit_asunto').value.trim(),
        descripcion: document.getElementById('edit_descripcion').value.trim(),
        progreso: document.getElementById('edit_progreso').value
    };

    try {
        const resp = await fetch(`/expedientes/${codigo}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (resp.ok) {
            alert(`¡Expediente ${codigo} actualizado correctamente!`);
            cerrarModal('modal-editar');
            cargarTablaExpedientes();
        } else {
            const err = await resp.json();
            alert(err.detail || "Error al actualizar expediente.");
        }
    } catch (error) {
        alert("Error al conectar con el servidor.");
    }
}

//  >>> modal reporte <<<
async function cargarReporte() {
    try {
        const resp = await fetch('/expedientes/reportes', {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const res = await resp.json();
            const tbody = document.getElementById('tabla-reporte-body');
            let html = '';

            res.data.forEach((item, index) => {
                html += `
                    <tr>
                        <td>${index + 1}</td>
                        <td><strong>${item.codigo}</strong></td>
                        <td>${item.nombre}</td>
                        <td><span class="badge-progreso">${item.estado_tramite}</span></td>
                    </tr>
                `;
            });

            tbody.innerHTML = html; //Inyecta en el tbody
            abrirModal('modal-reporte');
        } else {
            alert("No se pudo generar el reporte.");
        }
    } catch (error) {
        alert("Error de conexión.");
    }
}

// --- modal actualizar usuario ---
async function prepararEdicionUsuario(username) {
    try {
        const resp = await fetch(`/usuarios/${username}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            
            document.getElementById('edit_usr_username').value = data.username;
            document.getElementById('edit_usr_rol').value = data.rol;
            document.getElementById('edit_usr_nombre').value = data.nombreCompleto;
            document.getElementById('edit_usr_dni').value = data.dni;
            document.getElementById('edit_usr_correo').value = data.correo;
            document.getElementById('edit_usr_celular').value = data.celular;
            document.getElementById('edit_usr_direccion').value = data.direccion;

            abrirModal('modal-editar-usuario');
        } else {
            const err = await resp.json();
            alert(err.detail || "No se pudieron cargar los datos del usuario.");
        }
    } catch (error) {
        alert("Error de conexión al cargar el usuario.");
    }
}

async function procesarEdicionUsuario(e) {
    e.preventDefault();
    const username = document.getElementById('edit_usr_username').value;

    const payload = {
        rol: document.getElementById('edit_usr_rol').value,
        nombreCompleto: document.getElementById('edit_usr_nombre').value.trim(),
        dni: document.getElementById('edit_usr_dni').value.trim(),
        correo: document.getElementById('edit_usr_correo').value.trim(),
        celular: document.getElementById('edit_usr_celular').value.trim(),
        direccion: document.getElementById('edit_usr_direccion').value.trim()
    };

    try {
        const resp = await fetch(`/usuarios/${username}`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload)
        });

        if (resp.ok) {
            alert(`¡Datos del usuario ${username} actualizados correctamente!`);
            cerrarModal('modal-editar-usuario');
            if (typeof cargarTablaUsuarios === 'function') {
                cargarTablaUsuarios();
            }
        } else {
            const err = await resp.json();
            alert(err.detail || "Error al actualizar el usuario.");
        }
    } catch (error) {
        alert("Error al conectar con el servidor.");
    }
}