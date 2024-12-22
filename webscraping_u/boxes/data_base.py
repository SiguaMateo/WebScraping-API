try:
    import utils.data_base as data_base
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

url_login_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url_login'"""

user_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'user_name'"""

password_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'password'"""

url_home_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url_home'"""

insert_query = """INSERT INTO rptCajasProducidasUnosof_Dev VALUES (?,?,?,?,?,?)"""


def get_url_login():
    return data_base.get_value_from_db(url_login_query)

def get_user_login():
    return data_base.get_value_from_db(user_query)

def get_pass_login():
    return data_base.get_value_from_db(password_query)

def get_user_home():
    return data_base.get_value_from_db(url_home_query)

def get_insert_query():
    return insert_query