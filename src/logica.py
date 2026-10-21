import hashlib
from datetime import datetime
from datos import (
    leer_expedientes, guardar_expediente, actualizar_expediente_db, obtener_usuario,
    guardar_usuario, leer_usuarios, desactivar_usuario, activar_usuario_db, 
    actualizar_perfil, obtener_ultimo_codigo, actualizar_usuario, obtener_usuario_dni
)

# >>> USUARIO <<<
def cifrar_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar_usuario(username, password):
    user = obtener_usuario(username)
    if user and user[4] == "True":
        if user[2] == cifrar_password(password):
            return {"username": user[1], "rol": user[3], "dni": user[5], "nombreCompleto": user[6]} 
    return None

def verificar_admin(username):
    user = obtener_usuario(username)
    return user and user[3] == "admin" and user[4] == "True"

#Probar a hacer la validacion con "MENSAJE" en vez de true y false
def crear_usuario(username, password, rol, dni, nombreCompleto, correo, celular, direccion):
    if obtener_usuario(username):#Verifica que el username no se repita
        return "USERNAME_DUPLICADO"
    if obtener_usuario_dni(dni):
        return "DNI_DUPLICADO"
    
    guardar_usuario(username, cifrar_password(password), rol, dni, nombreCompleto, correo, celular, direccion, "True")
    return "OK"

def listar_usuarios(incluir_inactivos=False):
    todos = leer_usuarios()
    if incluir_inactivos:
        return todos
    else:
        # Filtra que el estado sea activo
        return [u for u in todos if u["estado"] == "True"]

def modificar_usuario(username, rol, dni, nombreCompleto, correo, celular, direccion):
    """Lógica para actualizar usuario validando que el DNI no le pertenezca a otra persona"""
    userdni = obtener_usuario_dni(dni)
    
    # Si el DNI existe pero le pertenece a un username distinto al que estamos editando
    if userdni and userdni[0] != username:
        return "DNI_DUPLICADO"
        
    actualizar_usuario(username, rol, dni, nombreCompleto, correo, celular, direccion)
    return "OK"

def eliminar_usuario(username, username_admin):
    if username == username_admin:#se valida que el admin no se elimine a si mismo por seguridad
        return False
    user = obtener_usuario(username)
    if user and user[4] == "True":
        desactivar_usuario(username)
        return True
    return False

def actualizar_perfil_usuario(username, correo, celular, direccion):
    """Lógica para que el usuario actualice sus datos de contacto"""
    # Aquí en el futuro podrías agregar validaciones extra si lo deseas
    actualizar_perfil(username, correo, celular, direccion)
    return True

def activar_usuario(username):
    user = obtener_usuario(username)
    if user and user[4] == "False":#se valida que su estado este como false osea eliminado
        activar_usuario_db(username)
        return True
    return False

def validar_dni(dni):
    """" isdigit valida que sea numeros | len(dni) que la length sea de 8"""
    return dni.isdigit() and len(dni) == 8

def buscar_usuario(username):
    """Buscar un usuario específico y retornarlo como diccionario"""
    u = obtener_usuario(username)
    # Verificamos que el usuario exista y esté activo (estado == "True")
    if u and u[4] == "True":
        return {
            "id": u[0], 
            "username": u[1], 
            "password": u[2], 
            "rol": u[3], 
            "estado": u[4], 
            "dni": u[5], 
            "nombreCompleto": u[6], 
            "correo": u[7], 
            "celular": u[8], 
            "direccion": u[9]
        }
    return None

# >>> Expediente <<<
def generar_codigo():
    ultimo_codigo = obtener_ultimo_codigo()
    if not ultimo_codigo:
        return "EXP-0001"

    partes = ultimo_codigo.split("-")
    if len(partes) == 2 and partes[1].isdigit():
        nuevo_numero = int(partes[1]) + 1 #lo convierte a int y lo suma
        #Hace que el formato sea 0001
        return f"EXP-{nuevo_numero:04d}"#:04d rellena con ceros a la izquierda hasta los 4 digitos
    return "EXP-0001"



def buscar_expediente(codigo):
    """Busca expedientes activos segun su codigo"""
    expedientes = leer_expedientes()
    for exp in expedientes:
        if exp[0].upper() == codigo.upper() and exp[12] == "True":
            return {
                "codigo": exp[0], "dni": exp[1], "nombreCompleto": exp[2],
                "correo": exp[3], "celular": exp[4], "direccion": exp[5],
                "tramite": exp[6], "asunto": exp[7], "descripcion": exp[8], "progreso": exp[9], 
                "fecha_creacion": exp[10], "fecha_modificacion": exp[11], "estado": exp[12],
                "usuario_username": exp[13]
            }
    return None

# Switch para ver inactivos y activos o solo activos | estado
def ordenar_expedientes(incluir_inactivos=False):
    """Ordena los expedientes alfabeticamente por codigo usando bubble sort"""
    if incluir_inactivos:
        expedientes = leer_expedientes()
    else:
        expedientes = [exp for exp in leer_expedientes() if exp[12] == "True"]
        
    n = len(expedientes)
    for i in range(n): 
        for j in range(0, n - i - 1):
            if expedientes[j][0] > expedientes[j + 1][0]:
                expedientes[j], expedientes[j + 1] = expedientes[j + 1], expedientes[j]
    return expedientes

def buscar_expediente_texto(texto):
    expedientes = leer_expedientes()
    resultados = []#crea lista vacia/arreglo unidimensional
    texto_limpio = texto.strip().lower()#lo hace lowercase y quita espacios
    for exp in expedientes:#recorre la lista
        if exp[12] == "True":
            nombre = exp[2].lower()
            asunto = exp[7].lower()
            descripcion = exp[8].lower()
            if texto_limpio in nombre or texto_limpio in asunto or texto_limpio in descripcion:
                resultados.append({"codigo": exp[0], "nombreCompleto": exp[2], "asunto": exp[7], "descripcion": exp[8]})
    return resultados

#arreglo paralelo
def generar_reporte():
    expedientes = leer_expedientes()
    array_codigos = []#Cada [] de estos es una lista simple/ arreglo unidimensional
    array_nombres = []
    array_progresos = []

    for exp in expedientes:
        if exp[12] == "True":
            array_codigos.append(exp[0])#agrega a la lista vacia
            array_nombres.append(exp[2])
            array_progresos.append(exp[9])

    reporte = []
    for i in range(len(array_codigos)):#recorre las listas para relacionar los datos por indice
        reporte.append({"codigo": array_codigos[i], "nombre": array_nombres[i], "estado_tramite": array_progresos[i]})#agrega a lista de reporte
    return reporte


def actualizar_expediente(codigo, correo, celular, direccion, tramite, asunto, descripcion, progreso):
    """Actualiza los datos de un expediente segun el codigo"""
    exp = buscar_expediente(codigo)
    if exp:
        fecha_mod = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        username = exp["usuario_username"]
        actualizar_perfil(username, correo, celular, direccion)
        actualizar_expediente_db(codigo, tramite, asunto, descripcion, progreso, fecha_mod, "True")
        return True
    return False

def desactivar_expediente(codigo):
    exp = buscar_expediente(codigo)
    if exp:
        fecha_mod = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        actualizar_expediente_db(codigo, exp["tramite"], exp["asunto"], exp["descripcion"], exp["progreso"], fecha_mod, "False")
        return True
    return False

def activar_expediente(codigo_buscado):
    expedientes = leer_expedientes()
    for exp in expedientes:
        if exp[0].upper() == codigo_buscado.upper() and exp[12] == "False":
            fecha_mod = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            actualizar_expediente_db(exp[0], exp[6], exp[7], exp[8], exp[9], fecha_mod, "True")
            return True
    return False