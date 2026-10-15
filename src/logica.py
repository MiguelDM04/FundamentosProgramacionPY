import hashlib
from datetime import datetime
from datos import (
    leer_expedientes, guardar_expediente, actualizar_expediente_db, obtener_usuario,
    guardar_usuario, leer_usuarios, desactivar_usuario, activar_usuario_db, 
    actualizar_usuario, obtener_ultimo_codigo
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

def crear_usuario(username, password, rol, dni, nombreCompleto, correo, celular, direccion):
    if obtener_usuario(username):#Verifica que el username no se repita
        return False
    guardar_usuario(username, cifrar_password(password), rol, dni, nombreCompleto, correo, celular, direccion, "True")
    return True

def listar_usuarios():
    return leer_usuarios()

def eliminar_usuario(username, username_admin):
    if username == username_admin:#se valida que el admin no se elimine a si mismo por seguridad
        return False
    user = obtener_usuario(username)
    if user and user[4] == "True":
        desactivar_usuario(username)
        return True
    return False

def activar_usuario(username):
    user = obtener_usuario(username)
    if user and user[4] == "False":#se valida que su estado este como false osea eliminado
        activar_usuario_db(username)
        return True
    return False

def validar_dni(dni):
    """" isdigit valida que sea numeros | len(dni) que la length sea de 8"""
    return dni.isdigit() and len(dni) == 8

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

def verificar_codigo(codigo):
    """Verifica si el codigo ya existe sea activo o inactivo"""
    expedientes = leer_expedientes()
    for exp in expedientes:
        if exp[0].upper() == codigo.upper():
            return True
    return False

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

def ordenar_expedientes():
    """Ordena los expedientes activos alfabeticamente por codigo usando bubble sort"""
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
    for i in range(len(array_codigos)):#recorre las listas al mismo tiempo para relacionar los datos por posicion
        reporte.append({"codigo": array_codigos[i], "nombre": array_nombres[i], "estado_tramite": array_progresos[i]})#agrega a lista de reporte
    return reporte


def actualizar_expediente(codigo, correo, celular, direccion, tramite, asunto, descripcion, progreso):
    """Actualiza los datos de un expediente segun el codigo"""
    exp = buscar_expediente(codigo)
    if exp:
        fecha_mod = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        username = exp["usuario_username"]
        actualizar_usuario(username, correo, celular, direccion)
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