from datos import leer_expedientes

"""" isdigit valida que sea numeros | len(dni) que la length sea de 8"""
def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8

"""Busca expedientes segun su codigo"""
def buscar_expediente(codigo_buscado):
    expedientes = leer_expedientes()
    for exp in expedientes:
        if exp[0].upper() == codigo_buscado.upper():
            return {"codigo": exp[0], "dni": exp[1], "nombreCompleto": exp[2], "tramite": exp[3]}
    return None

"""Ordena los expedientes alfabeticamente por codigo usando bubble sort"""
def ordenar_expedientes():
    expedientes = leer_expedientes()
    n = len(expedientes)
    for i in range(n): 
        for j in range(0, n - i - 1):
            if expedientes[j][0] > expedientes[j + 1] [0]:
                expedientes[j], expedientes[j + 1] = expedientes[j + 1], expedientes[j]
    return expedientes