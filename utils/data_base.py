try:
    from dotenv import load_dotenv
    import pyodbc
    import os
except Exception as e:
    print(f"Error al importar las librerias en data_base.py, {e}")

load_dotenv()

# Funciones para obtener cursores específicos de bases de datos
def data_base_conn_f():
    try:
        # Establecer la conexión
        conn_f = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={os.getenv("DATABASE_SERVER")};'
            f'DATABASE={os.getenv("DATABASE_NAME_F")};'
            f'UID={os.getenv("DATABASE_USER")};'
            f'PWD={os.getenv("DATABASE_PASSWORD")}'
        )
        cursor_f = conn_f.cursor()
        print(f"Conexión realizada con éxito a la base de datos: {conn_f}")
        return cursor_f
    except Exception as e:
        return None, None

def data_base_conn_u():
    try:
        # Establecer la conexión
        conn_u = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={os.getenv("DATABASE_SERVER")};'
            f'DATABASE={os.getenv("DATABASE_NAME_U")};'
            f'UID={os.getenv("DATABASE_USER")};'
            f'PWD={os.getenv("DATABASE_PASSWORD")}'
        )
        cursor_u = conn_u.cursor()
        print(f"Conexión realizada con éxito a la base de datos: {conn_u}")
        return cursor_u
    except Exception as e:
        return None, None

# Función para registrar logs en la base de datos
def log_to_db_f(id_group, log_level, message, endpoint, status_code):
    cursor_f = data_base_conn_f()
    if cursor_f:
        try:
            cursor_f.execute("""
                INSERT INTO Logs_Info (id_group, log_level, message, endpoint, status_code)
                VALUES (?, ?, ?, ?, ?)
            """, id_group, log_level, message, endpoint, status_code)
            cursor_f.commit()  # Commit en la conexión, no en el cursor
        except Exception as e:
            print(f"Error al registrar log en DB_F: {e}")

def log_to_db_u(id_group, log_level, message, endpoint, status_code):
    cursor_u = data_base_conn_u()
    if cursor_u:
        try:
            cursor_u.execute("""
                INSERT INTO Logs_Info (id_group, log_level, message, endpoint, status_code)
                VALUES (?, ?, ?, ?, ?)
            """, id_group, log_level, message, endpoint, status_code)
            cursor_u.commit()  # Commit en la conexión, no en el cursor
        except Exception as e:
            print(f"Error al registrar log en DB_U: {e}")

# Función para obtener un valor de la base de datos
def get_value_from_db_f(query):
    cursor_f = data_base_conn_f()
    if cursor_f:
        try:
            result = cursor_f.execute(query).fetchone()
            if result:
                return str(result[0])
            else:
                print(f"Error: No se encontró ningún resultado para la consulta: {query}")
                return None
        except Exception as e:
            print(f"Ocurrió un error al ejecutar la consulta: {e}")
            return None

def get_value_from_db_u(query):
    cursor_u = data_base_conn_u()
    if cursor_u:
        try:
            result = cursor_u.execute(query).fetchone()
            if result:
                return str(result[0])
            else:
                print(f"Error: No se encontró ningún resultado para la consulta: {query}")
                return None
        except Exception as e:
            print(f"Ocurrió un error al ejecutar la consulta: {e}")
            return None

user_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'user_mail'"""

password_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'password_mail'"""

server_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'domain_mail'"""

port_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'port'"""

target_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'mail_sis'"""

def get_user_mail():
    return get_value_from_db_f(user_mail_query)

def get_pass_mail():
    return get_value_from_db_f(password_mail_query)

def get_port_mail():
    return get_value_from_db_f(port_mail_query)

def get_server_mail():
    return get_value_from_db_f(server_mail_query)

def get_user_target():
    return get_value_from_db_f(target_mail_query)

