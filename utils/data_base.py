try:
    from dotenv import load_dotenv
    import pyodbc
    import os
except Exception as e:
    print(f"Error al importar las librerias en data_base.py, {e}")

load_dotenv()

def data_base_conn():
    try:
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={os.getenv("DATABASE_SERVER")};'
            f'DATABASE={os.getenv("DATABASE_NAME")};'
            f'UID={os.getenv("DATABASE_USER")};'
            f'PWD={os.getenv("DATABASE_PASSWORD")}'
        )
        cursor = conn.cursor()
        print(f"Conexion realizada con exito, {cursor}")
        return cursor
    except Exception as e:
        message = f"Error en la conexion con la base de datos, {e}"
        print(message)
    

def log_to_db(id_group, log_level, message, endpoint=None, status_code=None):
    with data_base_conn() as cursor:
        cursor.execute("""
            INSERT INTO Logs_Info (id_group, log_level, message, endpoint, status_code)
            VALUES (?, ?, ?, ?, ?)
        """, id_group, log_level, message, endpoint, status_code)
        data_base_conn().commit()

def get_value_from_db(query):
    """
    Función genérica para obtener un valor único de la base de datos.
    """
    try:
        result = data_base_conn().execute(query).fetchone()
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

port_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'domain_mail'"""

server_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'port'"""

target_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'mail_sis'"""

def get_user_mail():
    return get_value_from_db(user_mail_query)

def get_pass_mail():
    return get_value_from_db(password_mail_query)

def get_port_mail():
    return get_value_from_db(port_mail_query)

def get_server_mail():
    return get_value_from_db(server_mail_query)

def get_user_target():
    return get_value_from_db(target_mail_query)

