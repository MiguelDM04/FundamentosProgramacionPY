from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel, Field, EmailStr, field_validator
import re #para regex
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datos import inicializar_db, guardar_expediente, obtener_usuario
from logica import (
    buscar_expediente, ordenar_expedientes, 
    actualizar_expediente, desactivar_expediente,
    activar_expediente, verificar_admin, crear_usuario, 
    listar_usuarios, eliminar_usuario, activar_usuario,
    buscar_expediente_texto, generar_reporte, generar_codigo, 
    autenticar_usuario, buscar_usuario, modificar_usuario, actualizar_perfil_usuario
)

app = FastAPI(
    title="Mesa de Partes Digital",
    description="API con BD relacional desarrollada para desafio de Fundamentos de Programacion - Semana 09 - Grupo 01",
    version="2.1"
)

#Montar los archivos estaticos y las plantillas para usar con Jinja2Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates") 

# Inicializa la BD al ejecutar el server
inicializar_db()


# >>> validar rol <<<
def dependencia_admin(x_admin: str = Header(..., description="Ingresa tu usuario")):
    """Verifica que el usuario tenga el rol de amdin"""
    if not verificar_admin(x_admin):#Si el usuario no tiene admin
        raise HTTPException(status_code=403, detail="Acceso Denegado. Se requiere rol de administrador.")
    return x_admin

def dependencia_usuario(x_username: str = Header(..., description="Ingresa tu usuario")):
    """Verifica que el usuario exista y este activo"""
    if not x_username or not obtener_usuario(x_username):#Si esta vacio o si no encuentra el username da error
        raise HTTPException(status_code=401, detail="Usuario no válido o no autenticado.")
    return x_username

# Validacion de PYDANTIC | los example no sirven a menos que se use el /docs
class RegistroClienteRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=6)
    rol: str = Field(default="cliente", example="cliente o admin") # Valor por defecto 'cliente'
    dni: str = Field(..., min_length=8, max_length=8)
    nombreCompleto: str = Field(..., min_length=3)
    correo: EmailStr
    celular: str = Field(..., min_length=9, max_length=9)
    direccion: str = Field(..., min_length=5)

    @field_validator('username')
    def validar_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('El usuario solo debe contener letras, números o guion bajo.')
        return v

    @field_validator('dni')
    def validar_dni(cls, v):
        if not v.isdigit() or len(v) != 8:
            raise ValueError('El DNI debe tener exactamente 8 dígitos numéricos.')
        return v

    @field_validator('celular')
    def validar_celular(cls, v):
        if not re.match(r'^9\d{8}$', v):
            raise ValueError('El celular debe empezar con 9 y constar de 9 dígitos.')
        return v

    @field_validator('nombreCompleto')
    def validar_nombre(cls, v):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', v):
            raise ValueError('El nombre completo solo puede contener letras y espacios.')
        return v.strip()

class ExpedienteRequest(BaseModel):
    # codigo se genera automaticamente
    username_cliente: str = Field(default="", example="Requerido solo si el Admin registra por otra persona")
    tramite: str = Field(..., example="Licencia / Subvención / Queja")#Se usara como categoria para filtros en el frontend
    asunto: str = Field(..., example="Solicitud de licencia de funcionamiento")
    descripcion: str = Field(..., example="Descripcion del documento detallado...")

class ExpedienteUpdateRequest(BaseModel):
    correo: str = Field(..., example="nuevo_correo@email.com")
    celular: str = Field(..., example="987654321")
    direccion: str = Field(..., example="Nueva dirección 123")
    tramite: str = Field(..., example="Licencia")
    asunto: str = Field(..., example="Renovación de licencia")
    descripcion: str = Field(..., example="Solicito renovación...")
    progreso: str = Field(..., example="Recibido/ Confirmado/ En Revisión/ Atendido") # Puede ser Recibido, Confirmado, En Revisión, Atendido luego como cmbbox en frontend

class PerfilUpdatePayload(BaseModel):
    correo: str = Field(..., example="nuevo_correo@email.com")
    celular: str = Field(..., example="987654321")
    direccion: str = Field(..., example="Av. Las Flores 123")

class UsuarioUpdateRequest(BaseModel):
    rol: str = Field(..., example="cliente")
    dni: str = Field(..., min_length=8, max_length=8)
    nombreCompleto: str = Field(..., min_length=3)
    correo: EmailStr = Field(..., example="nuevo_correo@email.com")
    celular: str = Field(..., min_length=9, max_length=9)
    direccion: str = Field(..., example="Av. Las Flores 123")  

class LoginRequest(BaseModel):
    username: str = Field(..., example="maria0123")
    password: str = Field(..., example="claveSegura123")

# >>> RUTAS RENDER DE FRONTEND (JINJA2) <<<
@app.get("/", summary="Pagina de Login/Registro")
def render_auth(request: Request):
    return templates.TemplateResponse(request=request, name="auth.html")

@app.get("/inicio", summary="Pagina de Inicio")
def render_inicio(request: Request):
    return templates.TemplateResponse(request=request, name="inicio.html")

@app.get("/expedientes", summary="Gestion de Expedientes")
def render_expedientes(request: Request):
    return templates.TemplateResponse(request=request, name="expedientes.html")

@app.get("/usuarios", summary="Gestion de Usuarios")
def render_usuarios(request: Request):
    return templates.TemplateResponse(request=request, name="usuarios.html")

@app.get("/perfil", summary="Mi Perfil")
def render_perfil(request: Request):
    return templates.TemplateResponse(request=request, name="perfil.html")

# >>> AUTENTICACION <<<
@app.post("/login", summary="Validar usuario")
def r_login(credenciales: LoginRequest):
    """Autentica el usuario y devuelve los datos de sesion"""
    user = autenticar_usuario(credenciales.username, credenciales.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos, o cuenta inactiva.")
    return {"mensaje": "Login exitoso", "usuario": user}

@app.post("/registro", summary="Registro cliente")
def r_registro(nuevo_user: RegistroClienteRequest):
    """Registra un cliente/ciudadano validando duplicados de username y dni"""
    resultado = crear_usuario(
        nuevo_user.username, nuevo_user.password, "cliente", nuevo_user.dni, 
        nuevo_user.nombreCompleto, nuevo_user.correo, 
        nuevo_user.celular, nuevo_user.direccion
    )

    if resultado == "USERNAME_DUPLICADO":
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")
    elif resultado == "DNI_DUPLICADO":
        raise HTTPException(status_code=400, detail="El DNI ingresado ya se encuentra registrado.")
    
    return {"mensaje": f"Usuario {nuevo_user.username} registrado correctamente."}

# >>> USUARIOS <<<
@app.post("/usuarios/", summary="Crear nuevo usuario (Exclusivo Administrador)")
def r_crear_usuario(nuevo_user: RegistroClienteRequest, admin_user: str = Depends(dependencia_admin)):
    """Creacion de usuarios por el administrador validando duplicados"""
    
    resultado = crear_usuario(
        nuevo_user.username, nuevo_user.password, 
        nuevo_user.rol, nuevo_user.dni, nuevo_user.nombreCompleto, 
        nuevo_user.correo, nuevo_user.celular, nuevo_user.direccion
    )
    
    if resultado == "USERNAME_DUPLICADO":
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")
    elif resultado == "DNI_DUPLICADO":
        raise HTTPException(status_code=400, detail="El DNI ingresado ya se encuentra registrado.")      
    
    return {"mensaje": f"Usuario {nuevo_user.username} creado correctamente con rol '{nuevo_user.rol}'."}

@app.get("/usuarios/", summary="Ver lista de usuarios")
def r_obtener_usuarios(estado: str = "activos", admin_user: str = Depends(dependencia_admin)):
    """Retorna el listado y permite filtrar activos o todos"""
    incluir_inactivos = (estado == "todos")
    usuarios = listar_usuarios(incluir_inactivos)
    return {"total": len(usuarios), "usuarios": usuarios}

@app.get("/usuarios/{username}", summary="Consultar usuario por username")
def r_consultar_usuario(username: str, admin_user: str = Depends(dependencia_admin)):
    """Retorna los detalles de un usuario especifico"""
    # Validamos que el usuario exista
    usuario_encontrado = buscar_usuario(username)
    if not usuario_encontrado:
        raise HTTPException(
            status_code=404, 
            detail="Usuario no encontrado."
        )
    return usuario_encontrado

@app.put("/usuarios/{username}", summary="Actualizar usuario (Admin)")
def r_actualizar_usuario(username: str, datos: UsuarioUpdateRequest, admin_user: str = Depends(dependencia_admin)):
    """Actualiza la informacion del usuario"""
    if not obtener_usuario(username):
        raise HTTPException(status_code=404, detail="El usuario no existe.")
        
    resultado = modificar_usuario(
        username, datos.rol, datos.dni, datos.nombreCompleto, 
        datos.correo, datos.celular, datos.direccion
    )
    
    if resultado == "DNI_DUPLICADO":
        raise HTTPException(status_code=400, detail="El DNI ingresado ya pertenece a otro usuario registrado.")
    
    return {"mensaje": f"Usuario '{username}' actualizado correctamente."}

@app.delete("/usuarios/{username}", summary="Desactivar usuario")
def r_eliminar_usuario(username: str, admin_user: str = Depends(dependencia_admin)):
    """Aplica borrado logico a usuario activado"""
    if not eliminar_usuario(username, admin_user):
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario. Verifica que exista y este activo")
    return {"mensaje": "Usuario desactivado mediante borrado lógico."}

@app.patch("/usuarios/{username}/activar", summary="Reactivar usuario eliminado")
def r_activar_usuario(username: str, admin_user: str = Depends(dependencia_admin)):
    """Reactiva logicamente un usuario desactivado"""
    if not activar_usuario(username):
        raise HTTPException(status_code=404, detail="No se pudo activar el usuario. Verifique que exista y este desactivado.")
    return {"mensaje": "Usuario reactivado exitosamente."}

@app.get("/perfil/datos/{username}", summary="Obtener datos del propio perfil")
def r_obtener_mi_perfil(username: str, usuario: str = Depends(dependencia_usuario)):
    """Permite a un usuario consultar su propia informacion de perfil validando que sea su perfil si no es admin"""
    # Solo puede ver sus propios datos
    usuario_autenticado = obtener_usuario(usuario)
    rol = usuario_autenticado[3]
    
    if rol == "cliente" and usuario != username:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver este perfil.")
        
    perfil = buscar_usuario(username)
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado.")
        
    return perfil

@app.put("/perfil/{username}", summary="Actualizar perfil de usuario (Cliente y Admin)")
def r_actualizar_perfil(username: str, datos: PerfilUpdatePayload, usuario: str = Depends(dependencia_usuario)):
    """Permite al usuario actualizar sus datos de perfil/contacto"""
    usuario_autenticado = obtener_usuario(usuario)
    rol_autenticado = usuario_autenticado[3]

    # el cliente solo puede modificar su perfil
    if rol_autenticado == "cliente" and usuario != username:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. No tienes permisos para actualizar el perfil de otro usuario."
        )
        
    # Valida que el usuario exista
    if not obtener_usuario(username):
        raise HTTPException(
            status_code=404, 
            detail="El usuario que intenta actualizar no existe en la base de datos."
        )
        
    actualizar_perfil_usuario(username, datos.correo, datos.celular, datos.direccion)

    return {
        "mensaje": f"Perfil del usuario '{username}' actualizado correctamente por {rol_autenticado}."
    }


# >>> EXPEDIENTES <<<
@app.post("/expedientes/", summary="Registrar nuevo expediente")
def r_registrar_expediente(exp: ExpedienteRequest, usuario: str = Depends(dependencia_usuario)):
    """Registra un expediente generando un codigo automatico"""
    datos_usuario = obtener_usuario(usuario)
    rol = datos_usuario[3]

    # Verifica que si es cliente los datos se rellenen automaticamente
    if rol == "cliente":
        propietario_username = usuario
    else:
        if not exp.username_cliente:#En caso sea un admin ingresando un expediente y esta vacio
            raise HTTPException(status_code=400, detail="El Administrador debe especificar el username_cliente.")
        if not obtener_usuario(exp.username_cliente):#En caso sea admin y se equivoca de username
            raise HTTPException(status_code=404, detail="El username no es correcto.")
        propietario_username = exp.username_cliente

    # Genera el codigo del expediente
    nuevo_codigo = generar_codigo()
    # Obtiene la fecha para fecha_creacion y fecha_modificacion
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    guardar_expediente(
        nuevo_codigo, propietario_username, exp.tramite, exp.asunto, 
        exp.descripcion, "Recibido", fecha_actual, fecha_actual, "True"
    )
    return {"mensaje": "Expediente registrado exitosamente.", "codigo_generado": nuevo_codigo}

@app.get("/expedientes/", summary="Listar expedientes con bubble sort")
def r_listar_expedientes(estado: str = "activos", usuario: str = Depends(dependencia_usuario)):
    """Retorna los expedientes ordenados por codigo con bubble sort | filtra por usuario y por estado de expediente"""
    usuario_actual = obtener_usuario(usuario)
    rol = usuario_actual[3]
    
    incluir_inactivos = (estado == "todos")
    exp_ordenados = ordenar_expedientes(incluir_inactivos)
    
    if rol == "cliente":
        exp_ordenados = [exp for exp in exp_ordenados if exp[13] == usuario]
        
    return {"total": len(exp_ordenados), "expedientes": exp_ordenados}

@app.put("/expedientes/{codigo}", summary="Actualizar estado del expediente o contacto")
def r_actualizar_expediente(codigo: str, exp_upd: ExpedienteUpdateRequest, usuario: str = Depends(dependencia_admin)):
    """Actualiza el expediente verificando que exista y este activo"""
    exito = actualizar_expediente(codigo, exp_upd.correo, exp_upd.celular, exp_upd.direccion, exp_upd.tramite, exp_upd.asunto, exp_upd.descripcion, exp_upd.progreso)
    if not exito:
        raise HTTPException(status_code=404, detail="Expediente no existe o está inactivo.")
    return {"mensaje": f"Expediente {codigo} actualizado y notificado a los datos de contacto."}

@app.get("/expedientes/buscar/texto", summary="Busqueda de expedientes con texto")
def r_buscar_texto(palabra_clave: str, usuario: str = Depends(dependencia_admin)):
    """Busca segun el nombre completo, asunto, descripcion"""
    res = buscar_expediente_texto(palabra_clave)
    if not res: 
        raise HTTPException(status_code=404, detail="No se encontraron expedientes que contengan ese texto.")
    return {"total_encontrados": len(res), "resultados": res}

@app.get("/expedientes/reportes", summary="Generar reporte consolidado usando arreglos paralelos")
def r_reporte_expedientes(usuario: str = Depends(dependencia_admin)):
    """Genera un reporte usando arreglos paralelos"""
    reporte_data = generar_reporte()
    return {
        "total_registros": len(reporte_data),
        "data": reporte_data
    }


@app.get("/expedientes/{codigo}", summary="Consultar expediente por codigo")
def r_consultar_expediente(codigo: str, usuario: str = Depends(dependencia_usuario)):
    """Retorna los detalles del expediente validando que el cliente solo pueda ver los suyos y admin todos"""
    usuario_autenticado = obtener_usuario(usuario)
    rol_autenticado = usuario_autenticado[3]

    expediente = buscar_expediente(codigo)
    if not expediente:#validar que el expediente existe
        raise HTTPException(
            status_code=404, 
            detail="Expediente no encontrado o inactivo."
        )

    if rol_autenticado == "cliente" and usuario != expediente["usuario_username"]:#validar que el usuario sea el mismo del expediente
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. No tienes permisos para consultar el expediente de otro usuario."
        )

    return expediente

@app.delete("/expedientes/{codigo}", summary="Desactivar expediente")
def r_eliminar_expediente(codigo: str, usuario: str = Depends(dependencia_admin)):
    """Borrado logico a expediente activado"""
    if not desactivar_expediente(codigo): 
        raise HTTPException(status_code=404, detail="No se pudo desactivar. El expediente no existe.")
    return {"mensaje": f"Expediente {codigo} desactivado."}

@app.patch("/expedientes/{codigo}/activar", summary="Activar expediente")
def r_activar_expediente(codigo: str, usuario: str = Depends(dependencia_admin)):
    """Reactivado logico a expediente desactivado"""
    if not activar_expediente(codigo): 
        raise HTTPException(status_code=404, detail="No se pudo activar. Verifique si el código existe y está inactivo.")
    return {"mensaje": f"Expediente {codigo} activado."}