from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel, Field, EmailStr, field_validator
import re #para regex
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datos import inicializar_db, guardar_expediente, obtener_usuario, actualizar_usuario
from logica import (
    validar_dni, buscar_expediente, ordenar_expedientes, 
    actualizar_expediente, desactivar_expediente, verificar_codigo, 
    activar_expediente, verificar_admin, crear_usuario, 
    listar_usuarios, eliminar_usuario, activar_usuario,
    buscar_expediente_texto, generar_reporte, generar_codigo, autenticar_usuario
)

app = FastAPI(
    title="Mesa de Partes Digital",
    description="API con BD relacional desarrollada para avance desafio de Fundamentos de Programacion - Semana 09 - Grupo 01",
    version="2.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") 


# Inicializa la BD al ejecutar el server
inicializar_db()


# >>> SEGURIDAD <<<
def dependencia_admin(x_admin: str = Header(..., description="Ingresa tu usuario")):
    if not verificar_admin(x_admin):#Si el usuario no tiene admin
        raise HTTPException(status_code=403, detail="Acceso Denegado. Se requiere rol de administrador.")
    return x_admin

def dependencia_usuario(x_username: str = Header(..., description="Ingresa tu usuario")):
    if not x_username or not obtener_usuario(x_username):#Si esta vacio o si no encuentra el username da error
        raise HTTPException(status_code=401, detail="Usuario no válido o no autenticado.")
    return x_username

# Pydantic validacion
class RegistroClienteRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=6)
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

class UsuarioUpdatePayload(BaseModel):
    correo: str = Field(..., example="nuevo_correo@email.com")
    celular: str = Field(..., example="987654321")
    direccion: str = Field(..., example="Av. Las Flores 123")

class LoginRequest(BaseModel):
    username: str = Field(..., example="maria0123")
    password: str = Field(..., example="claveSegura123")

# >>> FRONTEND <<<
# Auth endpoints para las pantallas
@app.get("/", summary="Página de Login/Registro")
def render_auth(request: Request):
    return templates.TemplateResponse(request=request, name="auth.html")

@app.get("/inicio", summary="Página de Inicio")
def render_inicio(request: Request):
    return templates.TemplateResponse(request=request, name="inicio.html")

@app.get("/expedientes", summary="Gestion de Expedientes")
def render_expedientes(request: Request):
    return templates.TemplateResponse(request=request, name="expedientes.html")

@app.get("/expedientes/reportes", summary="Generar reporte consolidado usando arreglos paralelos")
def r_reporte_expedientes(usuario: str = Depends(dependencia_admin)):
    reporte_data = generar_reporte() # Llama directamente a la función existente en logica.py
    return {
        "total_registros": len(reporte_data),
        "data": reporte_data
    }

# Autenticacion
@app.post("/login", summary="Validar credenciales de usuario")
def r_login(credenciales: LoginRequest):
    user = autenticar_usuario(credenciales.username, credenciales.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos, o cuenta inactiva.")
    return {"mensaje": "Login exitoso", "usuario": user}

@app.post("/registro", summary="Registro nuevo cliente")
def r_registro(nuevo_user: RegistroClienteRequest):   
    exito = crear_usuario(
        nuevo_user.username, 
        nuevo_user.password, 
        "cliente", 
        nuevo_user.dni, 
        nuevo_user.nombreCompleto, 
        nuevo_user.correo, 
        nuevo_user.celular, 
        nuevo_user.direccion
    )
    if not exito:
        raise HTTPException(status_code=400, detail="El nombre de usuario o DNI ya está en uso.")
        
    return {"mensaje": f"Usuario {nuevo_user.username} registrado correctamente."}

# >>> USUARIOS <<<
@app.post("/usuarios/", summary="Crear nuevo usuario")
def r_crear_usuario(nuevo_user: RegistroClienteRequest, admin_user: str = Depends(dependencia_admin)):
    if not validar_dni(nuevo_user.dni):
        raise HTTPException(status_code=400, detail="DNI de usuario inválido. Debe tener 8 dígitos numéricos.")
    if not crear_usuario(nuevo_user.username, nuevo_user.password, nuevo_user.rol, nuevo_user.dni, nuevo_user.nombreCompleto, nuevo_user.correo, nuevo_user.celular, nuevo_user.direccion):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso.")
    return {"mensaje": f"Usuario {nuevo_user.username} creado correctamente."}

@app.get("/usuarios/", summary="Ver lista de usuarios")
def r_obtener_usuarios(admin_user: str = Depends(dependencia_admin)):
    usuarios = listar_usuarios()
    return {"total": len(usuarios), "usuarios": usuarios}

@app.delete("/usuarios/{username}", summary="Desactivar usuario")
def r_eliminar_usuario(username: str, admin_user: str = Depends(dependencia_admin)):
    if not eliminar_usuario(username, admin_user):
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario. Verifica que exista y este activo")
    return {"mensaje": "Usuario desactivado mediante borrado lógico."}

@app.patch("/usuarios/{username}/activar", summary="Reactivar usuario eliminado")
def r_activar_usuario(username: str, admin_user: str = Depends(dependencia_admin)):
    if not activar_usuario(username):
        raise HTTPException(status_code=404, detail="No se pudo activar el usuario. Verifique que exista y este desactivado.")
    return {"mensaje": "Usuario reactivado exitosamente."}

@app.put("/usuarios/{username}", summary="Actualizar perfil de usuario (Cliente y Admin)")
def r_actualizar_perfil(username: str, datos: UsuarioUpdatePayload, usuario: str = Depends(dependencia_usuario)):
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
    actualizar_usuario(username, datos.correo, datos.celular, datos.direccion)

    return {
        "mensaje": f"Perfil del usuario '{username}' actualizado correctamente por {rol_autenticado}."
    }

# >>> EXPEDIENTES <<<
@app.post("/expedientes/", summary="Registrar nuevo expediente")
def r_registrar_expediente(exp: ExpedienteRequest, usuario: str = Depends(dependencia_usuario)):
    datos_usuario = obtener_usuario(usuario)
    rol = datos_usuario[3]

    # Verifica que si es cliente los datos se rellenen automaticamente
    if rol == "cliente":
        propietario_username = usuario
    else:
        if not exp.username_cliente:#En caso sea un admin ingresando un expediente y esta vacio
            raise HTTPException(status_code=400, detail="El Administrador debe especificar el username_cliente para enlazar el trámite.")
        if not obtener_usuario(exp.username_cliente):#En caso sea admin y se equivoca de username
            raise HTTPException(status_code=404, detail="El cliente indicado no existe en la base de datos.")
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

@app.get("/expedientes/", summary="Listar expedientes (con el sort burbuja)")
def r_listar_expedientes(estado: str = "activos", usuario: str = Depends(dependencia_usuario)):
    usuario_actual = obtener_usuario(usuario)
    rol = usuario_actual[3]
    
    incluir_inactivos = (estado == "todos")
    exp_ordenados = ordenar_expedientes(incluir_inactivos)
    
    if rol == "cliente":
        exp_ordenados = [exp for exp in exp_ordenados if exp[13] == usuario]
        
    return {"total": len(exp_ordenados), "expedientes": exp_ordenados}

@app.get("/expedientes/buscar/texto", summary="Búsqueda de expedientes con texto")
def r_buscar_texto(palabra_clave: str, usuario: str = Depends(dependencia_admin)):
    res = buscar_expediente_texto(palabra_clave)
    if not res: 
        raise HTTPException(status_code=404, detail="No se encontraron expedientes que contengan ese texto.")
    return {"total_encontrados": len(res), "resultados": res}


@app.get("/expedientes/{codigo}", summary="Consultar expediente por código")
def r_consultar_expediente(codigo: str, usuario: str = Depends(dependencia_usuario)):

    usuario_autenticado = obtener_usuario(usuario)
    rol_autenticado = usuario_autenticado[3]

    expediente = buscar_expediente(codigo)
    if not expediente:#validar que el expediente existe
        raise HTTPException(
            status_code=404, 
            detail="Expediente no encontrado o inactivo."
        )

    user_usuario = expediente["usuario_username"]

    if rol_autenticado == "cliente" and usuario != user_usuario:#validar que el usuario sea el mismo del expediente
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. No tienes permisos para consultar el expediente de otro usuario."
        )

    return expediente


@app.put("/expedientes/{codigo}", summary="Actualizar estado del expediente y contacto")
def r_actualizar_expediente(codigo: str, exp_upd: ExpedienteUpdateRequest, usuario: str = Depends(dependencia_admin)):
    exito = actualizar_expediente(codigo, exp_upd.correo, exp_upd.celular, exp_upd.direccion, exp_upd.tramite, exp_upd.asunto, exp_upd.descripcion, exp_upd.progreso)
    if not exito:
        raise HTTPException(status_code=404, detail="Expediente no existe o está inactivo.")
    return {"mensaje": f"Expediente {codigo} actualizado y notificado a los datos de contacto."}

@app.delete("/expedientes/{codigo}", summary="Desactivar expediente")
def r_eliminar_expediente(codigo: str, usuario: str = Depends(dependencia_admin)):
    if not desactivar_expediente(codigo): 
        raise HTTPException(status_code=404, detail="No se pudo desactivar. El expediente no existe.")
    return {"mensaje": f"Expediente {codigo} desactivado."}

@app.patch("/expedientes/{codigo}/activar", summary="Activar expediente")
def r_activar_expediente(codigo: str, usuario: str = Depends(dependencia_admin)):
    if not activar_expediente(codigo): 
        raise HTTPException(status_code=404, detail="No se pudo activar. Verifique si el código existe y está inactivo.")
    return {"mensaje": f"Expediente {codigo} activado."}