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

insert_query = """INSERT INTO rptFresh_Portal_Ventas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_v_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 10 AND prm_descripcion = 'url_v'"""

delete_sales_query = """DELETE FROM rptFresh_Portal_Ventas
            WHERE vent_invoice_date > ?"""

def get_url_login():
    return data_base.get_value_from_db(url_login_query)

def get_User():
    return data_base.get_value_from_db(user_WSCVETS)

def get_Pass():
    return data_base.get_value_from_db(password_WSCVETS)

def get_insert_query():
    return insert_query

def get_url_v():
    return data_base.get_value_from_db(url_v_query)

def get_delete_query():
    return data_base.get_value_from_db(delete_sales_query)