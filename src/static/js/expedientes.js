document.addEventListener('DOMContentLoaded', () => {
    // Verifica el rol del usuario logueado
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

    //Lee el estado del dropdown de progreso 
    const selectProgreso = document.getElementById('filtro-progreso-select');
    const progreso = selectProgreso ? selectProgreso.value : "todos";

    try {
        const resp = await fetch(`/expedientes/?estado=${estado}&progreso=${progreso}`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            renderizarTabla(data.expedientes, tbody, rol);
        } else {
            tbody.innerHTML = `<tr><td colspan="7" class="error-cell">Error al obtener expedientes.</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="error-cell">Error de conexión.</td></tr>`;
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


        //Botones en caso esta activado o desactivado | solo admin
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
                    <button class="btn-thematic" style="background-color: #fef3c7; color: #d97706; border: 1px solid #fde68a;" title="Ver Evidencias" onclick="verEvidencias('${codigo}')">
                        <i class="fa-solid fa-paperclip"></i>
                    </button>
                `;
            } else {
                accionesHtml = `
                    <button class="btn-thematic btn-reactivate" title="Reactivar" onclick="activarExpediente('${codigo}')">
                        <i class="fa-solid fa-rotate-left"></i> Reactivar
                    </button>
                `;
            }
        } else {// Es cliente
            accionesHtml = `<button class="btn-thematic" style="background-color: #fef3c7; color: #d97706; border: 1px solid #fde68a;" title="Ver Evidencias" onclick="verEvidencias('${codigo}')">
                        <i class="fa-solid fa-paperclip"></i>
                    </button>`;
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
        // Se agarran todas las celdas que tienen la clase col-filtro
        const celdas = fila.querySelectorAll(".col-filtro");
        let coincide = false;
        
        celdas.forEach(celda => {
            const texto = celda.textContent || celda.innerText;
            if (texto.toUpperCase().indexOf(input) > -1) {//verifica que lo escrito este en la celda si encuentra = true
                coincide = true;
            }
        });

        fila.style.display = coincide ? "" : "none";//ocultas las filas que no coinciden con la busqueda
    });
}

//Confirmacion de desactivar
async function desactivarExpediente(codigo) {
    if (!confirm(`¿Está seguro de desactivar el expediente ${codigo}?`)) return;
    try {
        const resp = await fetch(`/expedientes/${codigo}`, { method: 'DELETE', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaExpedientes();
    } catch (e) { alert("Error"); }
}

//Confirmacion de activacion
async function activarExpediente(codigo) {
    if (!confirm(`¿Desea reactivar el expediente ${codigo}?`)) return;//`` se usa estas para poder usar ${} 
    try {
        const resp = await fetch(`/expedientes/${codigo}/activar`, { method: 'PATCH', headers: getAuthHeaders() });
        if (resp.ok) cargarTablaExpedientes();
    } catch (e) { alert("Error"); }
}


async function guardarExpediente(e) {
    e.preventDefault();
    const rol = sessionStorage.getItem('rol_activo');
    
    // Utilizamos FormData para poder adjuntar los archivos
    const formData = new FormData();
    formData.append('tramite', document.getElementById('exp_tramite').value);
    formData.append('asunto', document.getElementById('exp_asunto').value);
    formData.append('descripcion', document.getElementById('exp_descripcion').value);
    
    if (rol === 'admin') {
        const usernameCliente = document.getElementById('exp_username_cliente').value.trim();
        formData.append('username_cliente', usernameCliente);
    }

    // Obtenemos los archivos seleccionados
    const inputEvidencias = document.getElementById('exp_evidencias');
    const tiposPermitidos = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (inputEvidencias.files.length > 0) {
        for (let i = 0; i < inputEvidencias.files.length; i++) {
            const archivo = inputEvidencias.files[i];

            if(!tiposPermitidos.includes(archivo.type)){
                alert(`Error: El archivo "${archivo.name}" no es válido. Solo se permiten imágenes o documentos PDF.`);
                return;
            }
            formData.append('evidencias', archivo);
        }
    }

    try {
        const headers = getAuthHeaders();
        // Al enviar FormData, el navegador debe calcular el Content-Type automaticamente.
        delete headers['Content-Type']; 

        const resp = await fetch('/expedientes/', {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (resp.ok) {
            const res = await resp.json();
            alert(`¡Expediente registrado correctamente!\nCodigo del Expediente: ${res.codigo_generado}`);
            cerrarModal('modal-nuevo-expediente'); // Cuando se ejecute correctamente cierra modal
            document.getElementById('form-nuevo-expediente').reset();
            cargarTablaExpedientes();
        } else {
            const err = await resp.json();
            alert(err.detail || "Error al registrar expediente.");
        }
    } catch (error) { 
        alert("Error de conexión al guardar el expediente."); 
    }
}

//ver evidencias
async function verEvidencias(codigo) {
    document.getElementById('evi_codigo_titulo').innerText = codigo;
    const contenedor = document.getElementById('contenedor-lista-evidencias');
    contenedor.innerHTML = '<p class="loading-cell">Cargando evidencias...</p>';
    abrirModal('modal-evidencias');

    try {
        const resp = await fetch(`/expedientes/${codigo}/evidencias`, {
            headers: getAuthHeaders()
        });

        if (resp.ok) {
            const data = await resp.json();
            
            if (data.evidencias.length === 0) {
                contenedor.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">No hay evidencias adjuntas en este expediente.</p>';
                return;
            }

            let html = '';
            data.evidencias.forEach(archivo => {
                const esPdf = archivo.extension.toLowerCase().includes('pdf');
                const icono = esPdf ? 'fa-file-pdf' : 'fa-image';
                const colorIcono = esPdf ? 'var(--danger-color)' : 'var(--accent-color)';
                
                // Formatear tamaño
                const kb = (archivo.tamaño / 1024).toFixed(1);
                const tamañoTexto = kb > 1024 ? (kb / 1024).toFixed(2) + ' MB' : kb + ' KB';

                html += `
                    <div class="resultado-item" style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <i class="fa-solid ${icono}" style="font-size: 1.8rem; color: ${colorIcono};"></i>
                            <div style="display: flex; flex-direction: column;">
                                <span style="font-weight: 700; font-size: 0.9rem; color: var(--text-primary); word-break: break-all;">${archivo.nombre}</span>
                                <span style="font-size: 0.75rem; color: var(--text-secondary);">${tamañoTexto} • ${archivo.fecha_subida}</span>
                            </div>
                        </div>
                        <a href="${archivo.ruta}" target="_blank" class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem;">
                            <i class="fa-solid fa-eye"></i> Ver
                        </a>
                    </div>
                `;
            });
            contenedor.innerHTML = html;
        } else {
            contenedor.innerHTML = '<p style="color: var(--danger-color); text-align: center;">Error al obtener los archivos.</p>';
        }
    } catch (error) {
        contenedor.innerHTML = '<p style="color: var(--danger-color); text-align: center;">Error de conexión.</p>';
    }
}