from datos import leer_expedientes, rewrite_expedientes

def validar_dni(dni):
    """" isdigit valida que sea numeros | len(dni) que la length sea de 8"""
    return dni.isdigit() and len(dni) == 8

def buscar_expediente(codigo_buscado):
    """Busca expedientes activos segun su codigo"""
    expedientes = leer_expedientes()
    for exp in expedientes:
        if exp[0].upper() == codigo_buscado.upper() and exp[4] == "True":
            return {"codigo": exp[0], "dni": exp[1], "nombreCompleto": exp[2], "tramite": exp[3], "estado": exp[4]}
    return None

def ordenar_expedientes():
    """Ordena los expedientes activos alfabeticamente por codigo usando bubble sort"""
    expedientes = [exp for exp in leer_expedientes() if exp[4] == "True"]
    n = len(expedientes)
    for i in range(n): 
        for j in range(0, n - i - 1):
            if expedientes[j][0] > expedientes[j + 1] [0]:
                expedientes[j], expedientes[j + 1] = expedientes[j + 1], expedientes[j]
    return expedientes

def actualizar_expediente(codigo_buscado, nuevo_nombre, nuevo_tramite):
    """Actualiza los datos de un expediente segun el codigo"""
    expedientes = leer_expedientes()
    encontrado = False
    for exp in expedientes:
        if exp[0].upper() == codigo_buscado.upper() and exp[4] == "True":
            exp[2] = nuevo_nombre
            exp[3] = nuevo_tramite
            encontrado = True
            break
    if encontrado:
        rewrite_expedientes(expedientes)
        return True
    return False

def desactivar_expediente(codigo_buscado):
    """Cambia el estado a false para un delete logico"""
    expedientes = leer_expedientes()
    encontrado = False
    for exp in expedientes:
        if exp[0].upper() == codigo_buscado.upper() and exp[4] == "True":
            exp[4] = "False"
            encontrado = True
            break
    if encontrado:
        rewrite_expedientes(expedientes)
        return True
    return False