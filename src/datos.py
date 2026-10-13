import os
import sqlite3
import hashlib

db_name = "mesa_partes.db"

def conectar():
    """Crea y retorna la Conexion al archivo BD de SQLite"""
    return sqlite3.connect(db_name)

def inicializar_db():
    """Crea las tablas y se agrega un usuario admin default"""
    conexion = conectar()
    cursor = conexion.cursor()#Se usa para las consultas SQL

    # Tabla usuarios | se usan ''' para poder ponerlo en multiples lineas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, 
        rol TEXT NOT NULL,
        estado TEXT NOT NULL)
    ''')

    # Tabla expedientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expedientes(
        codigo TEXT PRIMARY KEY,
        dni TEXT NOT NULL,
        nombreCompleto TEXT NOT NULL,
        correo TEXT NOT NULL,
        tramite TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        progreso TEXT NOT NULL,
        fecha_creacion TEXT NOT NULL,
        fecha_modificacion TEXT NOT NULL,
        estado TEXT NOT NULL)
    ''')

    #Busca si hay un usuario ya creado si no hay los crea
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        #Cifrar contraseñas | sha256 lo transforma a una cadena de 64 caracteres aleatorios para seguridad
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()#encode lo cambia a bytes | hexdigest lo transforma a texto legible
        cliente_pass = hashlib.sha256("cliente123".encode()).hexdigest()

        cursor.execute("INSERT INTO usuarios (username, password, rol, estado) VALUES (?, ?, ?, ?)",
                        ("admin", admin_pass, "admin", "True"))
        cursor.execute("INSERT INTO usuarios (username, password, rol, estado) VALUES (?, ?, ?, ?)",
                        ("test", cliente_pass, "cliente", "True"))
        
    conexion.commit()#Confirma los cambios
    conexion.close()#Cierra conexion para liberar recursos


# >>>> CRUD usuario <<<<
def guardar_usuario(username, password, rol, estado="True"):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO usuarios (username, password, rol, estado) values (?, ?, ?, ?)",
                    (username, password, rol, estado))
    conexion.commit()
    conexion.close()

def obtener_usuario(username):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))#sin la coma da error | para que lo reciba como lista parametros
    user = cursor.fetchone()#Agarra uno
    conexion.close()
    return user

def leer_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()
    #No se devuelve la contraseña por seguridad
    cursor.execute("SELECT id, username, rol, estado FROM usuarios")
    usuarios = cursor.fetchall()
    conexion.close()
    #Para que fastapi y jinja2 lo lea mejor se convierte a diccionario
    return [{"id": u[0], "username": u[1], "rol": u[2], "estado": u[3]} for u in usuarios]

def desactivar_usuario(username):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET estado = 'False' WHERE username = ?", (username,))


# >>>> CRUD expedientes <<<<
def guardar_expediente(codigo, dni, nombreCompleto, correo, tramite, descripcion, progreso, fecha_creacion, fecha_modificacion, estado="True"):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO expedientes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (codigo, dni, nombreCompleto, correo, tramite, descripcion, progreso, fecha_creacion, fecha_modificacion, estado))
    conexion.commit()
    conexion.close()

def leer_expedientes():
    """"Leer todos los expedientes de la bd y lo retorna como lista de listas (para usar arrays)"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM expedientes")
    filas = cursor.fetchall()
    conexion.close()
    # Se convierte los registro de SQLite a listas para poder ordenar
    return [list(fila) for fila in filas]#recorre los registros y los convierte en una lista de python ['codigo', 'dni', etc]

def actualizar_expediente(codigo, dni, nombreCompleto, correo, tramite, descripcion, progreso, fecha_modificacion, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(''' 
        UPDATE expedientes
        SET dni=?, nombreCompleto=?, correo=?, tramite=?, descripcion=?, progreso=?, fecha_modificacion=?, estado=?
        WHERE codigo=?
    ''', (dni, nombreCompleto, correo, tramite, descripcion, progreso, fecha_modificacion, estado, codigo))
    conexion.commit()
    conexion.close()