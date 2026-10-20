document.addEventListener('DOMContentLoaded', () => {
    // Mostrar switch si es admin
    const rol = sessionStorage.getItem('rol_activo');
    if (rol === 'admin') {
        const filtros = document.querySelector('.filtros-secundarios');
        if (filtros) filtros.style.display = 'flex';
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'inline-flex');
    }
    
    cargarTablaExpedientes();
});

async function cargarTablaExpedientes() {
    const tbody = document.getElementById('tabla-expedientes-body');
    const rol = sessionStorage.getItem('rol_activo');
    
    // Leer el estado del switch
    const switchInactivos = document.getElementById('switch-inactivos');
    const estado = (switchInactivos && switchInactivos.checked) ? "todos" : "activos";

    try {
        const resp = await fetch(`/expedientes/?estado=${estado}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            renderizarTabla(data.expedientes, tbody, rol);
        } else {
            tbody.innerHTML = `<tr><td colspan="8" class="error-cell">Error al obtener expedientes.</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="8" class="error-cell">Error de conexión.</td></tr>`;
    }
}

function renderizarTabla(lista, tbody, rol) {
    if (!lista || lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-cell">No hay expedientes para mostrar.</td></tr>`;
        return;
    }

    let html = '';
    lista.forEach(exp => {
        const codigo = exp[0];
        const nombre = exp[2];
        const tramite = exp[6];
        const asunto = exp[7];
        const progreso = exp[9];
        const fechaM = exp[11]
        const activo = (exp[12] === "True");

        let classProgreso = 'badge-recibido';
        if (progreso === 'Confirmado') classProgreso = 'badge-confirmado';
        if (progreso === 'En Revisión') classProgreso = 'badge-revision';
        if (progreso === 'Atendido') classProgreso = 'badge-atendido';

        // Estilos para inactivos
        const filaClass = activo ? 'fila-expediente' : 'fila-expediente fila-inactiva';
        const badgeActivo = activo ? '<span class="badge-progreso badge-atendido">Activo</span>' : '<span class="badge-progreso" style="background:#fca5a5; color:#7f1d1d;">Inactivo</span>';

        let accionesHtml = '';
        if (rol === 'admin') {
            if (activo) {
                accionesHtml = `
                    <button class="btn-thematic btn-edit" title="Editar" onclick="prepararEdicion('${codigo}')">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="btn-thematic btn-delete" title="Desactivar" onclick="desactivarExpediente('${codigo}')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
            } else {
                accionesHtml = `
                    <button class="btn-thematic btn-reactivate" title="Reactivar" onclick="activarExpediente('${codigo}')">
                        <i class="fa-solid fa-rotate-left"></i> Reactivar
                    </button>
                `;
            }
        } else {
            accionesHtml = `<span style="font-size: 0.8rem; color: var(--text-secondary)">Solo Lectura</span>`;
        }

        html += `
            <tr class="${filaClass}">
                <td class="col-filtro"><strong>${codigo}</strong></td>
                <td class="col-filtro">${nombre}</td>
                <td class="col-filtro">${tramite}</td>
                <td class="col-filtro">${asunto}</td>
                <td><span class="badge-progreso ${classProgreso}">${progreso}</span></td>
                <td>${badgeActivo}</td>
                <td>${fechaM}</td>
                <td class="action-cells">${accionesHtml}</td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// BUSCADOR
function filtrarTablaGeneral() {
    const input = document.getElementById("filtro-general").value.toUpperCase();
    const filas = document.querySelectorAll(".fila-expediente");

    filas.forEach(fila => {
        // Obtenemos todas las celdas que tienen la clase col-filtro
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

async function desactivarExpediente(codigo) {
    if (!confirm(`¿Está seguro de desactivar el expediente ${codigo}?`)) return;
    try {
        const resp = await fetch(`/expedientes/${codigo}`, { method: 'DELETE', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaExpedientes();
    } catch (e) { alert("Error"); }
}

async function activarExpediente(codigo) {
    if (!confirm(`¿Desea reactivar el expediente ${codigo}?`)) return;
    try {
        const resp = await fetch(`/expedientes/${codigo}/activar`, { method: 'PATCH', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaExpedientes();
    } catch (e) { alert("Error"); }
}

async function guardarExpediente(e) {
    e.preventDefault();
    const rol = sessionStorage.getItem('rol_activo');
    const payload = {
        tramite: document.getElementById('exp_tramite').value,
        asunto: document.getElementById('exp_asunto').value,
        descripcion: document.getElementById('exp_descripcion').value
    };
    if (rol === 'admin') payload.username_cliente = document.getElementById('exp_username_cliente').value;

    try {
        const resp = await fetch('/expedientes/', { method: 'POST', headers: getAuthHeaders(), body: JSON.stringify(payload) });
        if (resp.ok) {
            cerrarModal('modal-nuevo-expediente');
            document.getElementById('form-nuevo-expediente').reset();
            cargarTablaExpedientes();
        } else {
            alert("Error al registrar");
        }
    } catch (error) { alert("Error"); }
}