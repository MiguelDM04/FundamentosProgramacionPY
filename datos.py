import os

archivo_datos = "expedientes.txt"

""" Guardar expediente en un archivo de texto"""
def guardar_expediente(codigo, dni, nombreCompleto, tramite, estado=True):
    linea = f"{codigo},{dni},{nombreCompleto},{tramite},{estado}\n"
    with open(archivo_datos, "a", encoding="utf-8") as archivo:
        archivo.write(linea)

""""Leer todos los expedientes del archivo y lo retorna como lista de diccionarios"""
def leer_expedientes():
    expedientes = []
    if os.path.exists(archivo_datos):
        with open(archivo_datos, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.strip().split(",")
                if len(partes) == 5:
                    expedientes.append(partes)
    return expedientes

"""Sobreescribe el archivo completo"""
def rewrite_expedientes(lista_expedientes):
    with open(archivo_datos, "w", encoding="utf-8") as archivo:
        for exp in lista_expedientes:
            linea = f"{exp[0]}, {exp[1]}, {exp[2]}, {exp[3]}, {exp[4]}\n"
            archivo.write(linea)
