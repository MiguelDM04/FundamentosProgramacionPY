import os
import sqlite3
import hashlib

db_name = "mesa_partes.db"
#Para ver comentarios de """ en la consola de una funcion
#cd src -> py -> import file.py -> print(file.funcion.__doc__)

def conectar():
    """Crea y retorna la conexion al archivo BD de SQLite"""
    return sqlite3.connect(db_name)

def inicializar_db():
    """Crea las tablas y agrega dos usuarios en caso no exista ninguno"""
    conexion = conectar()
    cursor = conexion.cursor()#Se usa para las consultas SQL

    # se usa text en todo porque no es necesario usar los otros tipos de datos con sqlite
    # Tabla usuarios | se usan ''' para poder ponerlo en multiples lineas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, 
        rol TEXT NOT NULL,
        estado TEXT NOT NULL,
        dni TEXT UNIQUE NOT NULL,
        nombreCompleto TEXT NOT NULL,
        correo TEXT NOT NULL,
        celular TEXT NOT NULL,
        direccion TEXT NOT NULL)
    ''')

    # Tabla expedientes 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expedientes(
        codigo TEXT PRIMARY KEY,
        usuario_username TEXT NOT NULL,
        tramite TEXT NOT NULL,
        asunto TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        progreso TEXT NOT NULL,
        fecha_creacion TEXT NOT NULL,
        fecha_modificacion TEXT NOT NULL,
        estado TEXT NOT NULL,
        FOREIGN KEY (usuario_username) REFERENCES usuarios(username)
    )
    ''')

    #Busca si hay un usuario ya creado si no hay los crea
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        #Cifrar contraseñas | sha256 lo transforma a una cadena de 64 caracteres aleatorios para seguridad
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()#encode lo cambia a bytes | hexdigest lo transforma a texto legible
        cliente_pass = hashlib.sha256("cliente123".encode()).hexdigest()

        cursor.execute("INSERT INTO usuarios (username, password, rol, estado, dni, nombreCompleto, correo, celular, direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("admin", admin_pass, "admin", "True", "33344441", "Miguel Deza", "miguel@municipalidad.gob.pe", "964238923", "Jaime de mimbela"))
        cursor.execute("INSERT INTO usuarios (username, password, rol, estado, dni, nombreCompleto, correo, celular, direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("test", cliente_pass, "cliente", "True", "12345678", "Juan Perez", "juan.perez@gmail.com", "987654321", "Av. Los Rosales 123"))
        
    conexion.commit()#Confirma los cambios
    conexion.close()#Cierra conexion para liberar recursos


# >>>> CRUD usuarios <<<<
def guardar_usuario(username, password, rol, dni, nombreCompleto, correo, celular, direccion, estado="True"):
    """Inserta un usuario en la BD"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO usuarios (username, password, rol, estado, dni, nombreCompleto, correo, celular, direccion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (username, password, rol, estado, dni, nombreCompleto, correo, celular, direccion))
    conexion.commit()
    conexion.close()

def obtener_usuario(username):
    """Obtiene un usuario especifico usando el username BD"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))#sin la coma da error | para que lo reciba como lista parametros
    user = cursor.fetchone()#Agarra uno
    conexion.close()
    return user

def obtener_usuario_dni(dni):
    """Busca y retorna el username de usuarios segun su DNI BD"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT username FROM usuarios WHERE dni = ?", (dni,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def leer_usuarios():
    """Lee todos los usuarios sin mostrar contraseñas por seguridad y retorna una lista de diccionarios"""
    #usuarios = [{"nombre":"miguel", "dni":7437472},{"nombre":"andre", "dni":3123123}] <- lista diccionarios
    conexion = conectar()
    cursor = conexion.cursor()
    #No se devuelve la contraseña por seguridad
    cursor.execute("SELECT id, username, rol, estado, dni, nombreCompleto, correo, celular, direccion FROM usuarios")
    usuarios = cursor.fetchall()
    conexion.close()
    #Para que fastapi y jinja2 lo lea mejor se convierte a diccionario | arreglo unidimensional
    return [{"id": u[0], "username": u[1], "rol": u[2], "estado": u[3], "dni": u[4], "nombreCompleto": u[5], "correo": u[6], "celular": u[7], "direccion": u[8]} for u in usuarios]

def desactivar_usuario(username):
    """Hace un borrado logico del usuario actualizando su estado a False"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET estado = 'False' WHERE username = ?", (username,))
    conexion.commit()
    conexion.close()

def activar_usuario_db(username):
    """Activa logicamente el usuario actualizando su estado a True"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET estado = 'True' WHERE username = ?", (username,))
    conexion.commit()
    conexion.close()

#En caso el cliente cambia de correo, celular o direccion lo puede actualizar en su perfil
def actualizar_perfil(username, correo, celular, direccion):
    """Actualiza los datos de contacto del usuario"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE usuarios SET correo = ?, celular = ?, direccion = ? WHERE username = ?", (correo, celular, direccion, username))
    conexion.commit()
    conexion.close()  

def actualizar_usuario(username, rol, dni, nombreCompleto, correo, celular, direccion):
    """Actualiza la informacion de un usuario (solo admin)"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE usuarios 
        SET rol = ?, dni = ?, nombreCompleto = ?, correo = ?, celular = ?, direccion = ? 
        WHERE username = ?
    ''', (rol, dni, nombreCompleto, correo, celular, direccion, username))
    conexion.commit()
    conexion.close()


# >>>> CRUD expedientes <<<<
def guardar_expediente(codigo, usuario_username, tramite, asunto, descripcion, progreso, fecha_creacion, fecha_modificacion, estado="True"):
    """Inserta un nuevo expediente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO expedientes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (codigo, usuario_username, tramite, asunto, descripcion, progreso, fecha_creacion, fecha_modificacion, estado))
    conexion.commit()
    conexion.close()

def leer_expedientes():
    """"Lee todos los expedientes de la tabla tambien usando inner join usuario y lo retorna como lista de listas"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        SELECT 
            e.codigo, u.dni, u.nombreCompleto, u.correo, u.celular, u.direccion, 
            e.tramite, e.asunto, e.descripcion, e.progreso, 
            e.fecha_creacion, e.fecha_modificacion, e.estado, e.usuario_username
        FROM expedientes e
        INNER JOIN usuarios u ON e.usuario_username = u.username
    ''')
    filas = cursor.fetchall()
    conexion.close()
    # Se convierte los registro de SQLite a listas para poder ordenar | arreglo bidimensional
    return [list(fila) for fila in filas]#cada conjunto de datos lo convierte en una lista independiente, osea una lista de listas


def actualizar_expediente_db(codigo, tramite, asunto, descripcion, progreso, fecha_modificacion, estado):
    """Actualiza el expediente"""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(''' 
        UPDATE expedientes
        SET tramite=?, asunto=?, descripcion=?, progreso=?, fecha_modificacion=?, estado=?
        WHERE codigo=?
    ''', (tramite, asunto, descripcion, progreso, fecha_modificacion, estado, codigo))
    conexion.commit()
    conexion.close()

#Funcion para obtener el ultimo registro y extraer su numero para sumarlo y asignarlo al nuevo expediente
def obtener_ultimo_codigo():
    """Obtiene último código de expediente registrado en la BD"""
    conexion = conectar()
    cursor = conexion.cursor()
    # Ordena de forma descendente y obtiene solo un codigo
    cursor.execute("SELECT codigo FROM expedientes ORDER BY codigo DESC LIMIT 1")
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None #devuelve el codigo si no no retorna nada