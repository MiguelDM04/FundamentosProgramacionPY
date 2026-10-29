document.addEventListener('DOMContentLoaded', () => {
    const rol = sessionStorage.getItem('rol_activo');
    if (rol !== 'admin') {
        alert("Acceso denegado. Redirigiendo...");
        window.location.href = "/inicio";
        return;
    }
    cargarTablaUsuarios();
});

// obtiene datos del server con estado
async function cargarTablaUsuarios() {
    const tbody = document.getElementById('tabla-usuarios-body');
    const switchInactivos = document.getElementById('switch-inactivos-usuarios');
    const estado = (switchInactivos && switchInactivos.checked) ? "todos" : "activos";
    
    try {
        const resp = await fetch(`/usuarios/?estado=${estado}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            renderizarTablaUsuarios(data.usuarios);
        } else {
            tbody.innerHTML = `<tr><td colspan="7" class="error-cell">Error al obtener usuarios.</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="error-cell">Error de conexión.</td></tr>`;
    }
}

// Tabla
function renderizarTablaUsuarios(listaUsuarios) {
    const tbody = document.getElementById('tabla-usuarios-body');

    if (!listaUsuarios || listaUsuarios.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">No hay usuarios para mostrar.</td></tr>`;
        return;
    }

    let html = '';
    listaUsuarios.forEach(usr => {
        const activo = (usr.estado === "True");
        
        const badgeRol = usr.rol === 'admin' 
            ? `<span class="badge badge-admin">Admin</span>` 
            : `<span class="badge badge-cliente">Cliente</span>`;
            
        const badgeEstado = activo 
            ? `<span class="badge-progreso badge-atendido">Activo</span>` 
            : `<span class="badge-progreso" style="background:#fca5a5; color:#7f1d1d;">Inactivo</span>`;
            
        const filaClass = activo ? 'fila-usuario' : 'fila-usuario fila-inactiva';

        let accionesHtml = '';
        if (activo) {
            accionesHtml = `
                <button class="btn-thematic btn-edit" title="Editar" onclick="prepararEdicionUsuario('${usr.username}')">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-thematic btn-delete" title="Desactivar" onclick="desactivarUsuario('${usr.username}')">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
        } else {
            accionesHtml = `
                <button class="btn-thematic btn-reactivate" title="Reactivar" onclick="activarUsuario('${usr.username}')">
                    <i class="fa-solid fa-rotate-left"></i> Reactivar
                </button>
            `;
        }

        html += `
            <tr class="${filaClass}">
                <td class="col-filtro"><strong>${usr.username}</strong></td>
                <td class="col-filtro">${usr.nombreCompleto}</td>
                <td class="col-filtro">${usr.dni}</td>
                <td>${badgeRol}</td>
                <td class="col-filtro">${usr.correo}</td>
                <td>${badgeEstado}</td>
                <td class="action-cells">${accionesHtml}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// Buscador
function filtrarTablaUsuarios() {
    const input = document.getElementById("filtro-usuarios").value.toUpperCase();
    const filas = document.querySelectorAll(".fila-usuario");

    filas.forEach(fila => {
        const celdas = fila.querySelectorAll(".col-filtro");
        let coincide = false;
        
        celdas.forEach(celda => {
            const texto = celda.textContent || celda.innerText;
            if (texto.toUpperCase().indexOf(input) > -1) {
                coincide = true;
            }
        });

        fila.style.display = coincide ? "" : "none";
    });
}

// CDA (create delete activate)
async function guardarNuevoUsuario(e) {
    e.preventDefault();
    
    const payload = {
        username: document.getElementById('usr_username').value.trim(),
        password: document.getElementById('usr_password').value,
        rol: document.getElementById('usr_rol').value,
        dni: document.getElementById('usr_dni').value.trim(),
        nombreCompleto: document.getElementById('usr_nombre').value.trim(),
        correo: document.getElementById('usr_correo').value.trim(),
        celular: document.getElementById('usr_celular').value.trim(),
        direccion: document.getElementById('usr_direccion').value.trim()
    };

    try {
        const resp = await fetch('/usuarios/', { 
            method: 'POST', 
            headers: getAuthHeaders(), 
            body: JSON.stringify(payload) 
        });
        
        if (resp.ok) {
            cerrarModal('modal-nuevo-usuario');
            document.getElementById('form-nuevo-usuario').reset();
            cargarTablaUsuarios(); 
        } else {
            const err = await resp.json();
            if (Array.isArray(err.detail)) {
                alert("Error en el formulario: " + err.detail[0].msg);
            } else {
                alert(err.detail || "Ocurrio un error inesperado")
            }
            
        } 
    } catch (error) { alert("Error de conexión."); }
}

async function desactivarUsuario(username) {
    if (!confirm(`¿Está seguro de desactivar al usuario ${username}?`)) return;
    try {
        const resp = await fetch(`/usuarios/${username}`, { method: 'DELETE', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaUsuarios();
        else alert("No se pudo desactivar el usuario.");
    } catch (e) { alert("Error de conexión"); }
}

async function activarUsuario(username) {
    if (!confirm(`¿Desea reactivar al usuario ${username}?`)) return;
    try {
        const resp = await fetch(`/usuarios/${username}/activar`, { method: 'PATCH', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaUsuarios();
        else alert("No se pudo reactivar el usuario.");
    } catch (e) { alert("Error de conexión"); }
}