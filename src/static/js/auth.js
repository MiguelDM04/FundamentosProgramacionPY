// Control de deslizamiento de los overlay 
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('container');
    const btnRegistro = document.getElementById('registro');
    const btnInicioSesion = document.getElementById('inicioSesion');

    btnRegistro.addEventListener('click', () => {
        container.classList.add("right-panel-active");
    });

    btnInicioSesion.addEventListener('click', () => {
        container.classList.remove("right-panel-active");
    });

    // Cargar tema guardado
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
    }
});

// Cambiar Tema Oscuro/Claro
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

// inicio sesion
async function procesarLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login_username').value;
    const password = document.getElementById('login_password').value;

    try {
        const resp = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (resp.ok) {
            const data = await resp.json();
            // Guardamos usuario activo en la sesión del navegador para usarlo en otras pantallas
            sessionStorage.setItem('usuario_activo', data.usuario.username);
            sessionStorage.setItem('rol_activo', data.usuario.rol);
            // Redirigir a inicio
            window.location.href = "/inicio";
        } else {
            const err = await resp.json();
            alert(err.detail || "Credenciales incorrectas.");
        }
    } catch (error) {
        alert("Error de conexión con el servidor.");
    }
}

//Validar datos registro | en caso falle detiene el proceso desde el backend
function validarDatosRegistro(data) {
    const regexDNI = /^[0-9]{8}$/;
    const regexCelular = /^9[0-9]{8}$/;
    const regexCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const regexNombre = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{3,100}$/;
    const regexUsername = /^[a-zA-Z0-9_]{4,20}$/;

    if (!regexUsername.test(data.username)) {
        alert("El usuario debe tener entre 3 y 20 caracteres, y solo puede tener letras, numero o guion bajo.");
        return false;
    }
    if (data.password.length < 5) {
        alert("La contraseña debe tener al menos 5 caracteres.");
        return false;
    }
    if (!regexDNI.test(data.dni)) {
        alert("El DNI debe contener exactamente 8 dígitos numéricos.");
        return false;
    }
    if (!regexNombre.test(data.nombreCompleto)) {
        alert("El nombre completo solo debe contener letras y espacios.");
        return false;
    }
    if (!regexCorreo.test(data.correo)) {
        alert("Ingrese un correo electrónico válido.");
        return false;
    }
    if (!regexCelular.test(data.celular)) {
        alert("El número de celular debe empezar con 9 y tener 9 dígitos.");
        return false;
    }
    if (data.direccion.trim().length < 5) {
        alert("La dirección ingresada es demasiado corta.");
        return false;
    }
    return true;
}

// registrar
async function procesarRegistro(e) {
    e.preventDefault();

    const payload = {
        username: document.getElementById('reg_username').value.trim(),
        password: document.getElementById('reg_password').value,
        dni: document.getElementById('reg_dni').value.trim(),
        nombreCompleto: document.getElementById('reg_nombreCompleto').value.trim(),
        correo: document.getElementById('reg_correo').value.trim(),
        celular: document.getElementById('reg_celular').value.trim(),
        direccion: document.getElementById('reg_direccion').value.trim()
    };

    // Validación local de los datos ingresados
    if (!validarDatosRegistro(payload)) {
        return;
    }

    try {
        const resp = await fetch('/registro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (resp.ok) {
            alert("¡Cuenta creada exitosamente! Por favor inicia sesión.");
            document.getElementById('container').classList.remove("right-panel-active");
            document.getElementById('registroForm').reset();
        } else {
            const err = await resp.json();
            alert(err.detail || "Error al registrar la cuenta.");
        }
    } catch (error) {
        alert("Error de conexión con el servidor.");
    }
}