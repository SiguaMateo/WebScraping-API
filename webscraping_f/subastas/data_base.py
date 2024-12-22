try:
    import utils.data_base as data_base
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

url_login_query = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'url_login'"""

user_WSCVETS = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'user_name'"""

password_WSCVETS = """SELECT prm_valor 
                        FROM dbo.Parametros_Sistema
                        WHERE id_grupo = 1 AND prm_descripcion LIKE 'password'"""

insert_query = """INSERT INTO rptFresh_Portal_Subastas_Dev_Test VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_s_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 13 AND prm_descripcion = 'url_s'"""
    
def get_url_login():
    return data_base.get_value_from_db(url_login_query)

def get_user_login():
    return data_base.get_value_from_db(user_WSCVETS)

def get_pass_login():
    return data_base.get_value_from_db(password_WSCVETS)

def get_url_s():
    return data_base.get_value_from_db(url_s_query)

def get_insert_query():
    return insert_query