document.addEventListener('DOMContentLoaded', () => {
    // Recuperar datos de la sesión activa guardada durante el Login
    const usuarioActivo = sessionStorage.getItem('usuario_activo') || 'Usuario';
    const rolActivo = sessionStorage.getItem('rol_activo') || 'cliente';

    // Inyectar el nombre del usuario
    const Inombre = document.getElementById('nombre-usuario');
    if (Inombre) {
        Inombre.textContent = usuarioActivo;
    }
    
    const badge = document.getElementById('rol-badge');
    const boxCliente = document.getElementById('descripcion-cliente');
    const boxAdmin = document.getElementById('descripcion-admin');

    // Segun el rol mostrar una o la otra
    if (rolActivo === 'admin') {
        if (badge) {
            badge.textContent = 'Administrador';
            badge.classList.add('badge-admin');
        }
        if (boxAdmin) boxAdmin.style.display = 'block';
    } else {
        if (badge) {
            badge.textContent = 'Ciudadano / Cliente';
            badge.classList.add('badge-cliente');
        }
        if (boxCliente) boxCliente.style.display = 'block';
    }
});