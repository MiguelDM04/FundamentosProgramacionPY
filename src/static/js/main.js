
document.addEventListener('DOMContentLoaded', () => {
    // Validar autenticacion de sesion
    const usuarioActivo = sessionStorage.getItem('usuario_activo');
    const rolActivo = sessionStorage.getItem('rol_activo');

    // Si el usuario no ha iniciado sesion, redirigir al auth para registro o login 
    if (!usuarioActivo && window.location.pathname !== '/') {
        window.location.href = '/';
        return;
    }

    // Visibilidad por rol
    const navUsuarios = document.getElementById('nav-usuarios');
    if (navUsuarios) {
        if (rolActivo === 'admin') {
            navUsuarios.style.display = 'flex';
        } else {
            navUsuarios.style.display = 'none'; // Ocultar para rol cliente
        }
    }

    // guardar tema ligh / dark
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
    }
});

// Función para cambiar de tema
function toggleTheme() {
    const body = document.body;
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Función cerrar sesion
function cerrarSesion() {
    if (confirm("¿Estás seguro de que deseas cerrar sesión?")) {
        sessionStorage.clear();
        window.location.href = "/";
    }
}

// Helper global para peticiones fetch con Header x-username
function getAuthHeaders() {
    const usuario = sessionStorage.getItem('usuario_activo') || '';
    const rol = sessionStorage.getItem('rol_activo') || '';
    
    const headers = {
        'Content-Type': 'application/json',
        'x-username': usuario
    };

    if (rol === 'admin') {
        headers['x-admin'] = usuario;
    }

    return headers;
}