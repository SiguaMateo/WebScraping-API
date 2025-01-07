try:
    from utils.data_base import get_value_from_db_u, data_base_conn_u
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

# def create_table_curstomers():
#     cursor = data_base_conn_u()
#     try:
#         with cursor:
#             cursor.execute("""
#                 IF EXISTS (SELECT * FROM sysobjects WHERE name='rptUnosof_Customers_Dev_Test' AND xtype='U')
#                 BEGIN
#                     DROP TABLE rptUnosof_Customers_Dev_Test
#                 END
#             """)
#             cursor.commit()
#             cursor.execute("""
#                 CREATE TABLE rptUnosof_Customers_Dev_Test(
#                     cus_id INT PRIMARY KEY,
#                     cus_market NVARCHAR(50),
#                     cus_opening_date DATE,
#                     cus_credit_limit FLOAT,
#                     cus_term NVARCHAR(40),
#                     cus_ruc_resale NVARCHAR(30),
#                     cus_customer NVARCHAR(100),
#                     cus_parent_billing NVARCHAR(150),
#                     cus_parent_trading NVARCHAR(150),
#                     cus_flow NVARCHAR(20),
#                     cus_shipping_address NVARCHAR(150),
#                     cus_cargo_agency NVARCHAR(50),
#                     cus_incoterm NVARCHAR(15),
#                     cus_sales_rep NVARCHAR(30),
#                     cus_phone NVARCHAR(MAX),
#                     cus_city NVARCHAR(40),
#                     cus_country NVARCHAR(40),
#                     cus_sri_country INT,
#                     cus_created NVARCHAR(30)
#                 )
#             """)
#             cursor.commit()
#     except Exception as e:
#         message = f"Error al crear la tabla, {e}"
#         print(message)

# create_table_curstomers()


url_login_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url_login'"""

user_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'user_name'"""

password_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'password'"""

url_cst_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 11 AND prm_descripcion = 'url_cst'"""

insert_query = """INSERT INTO rptUnosof_Customers_Dev VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

delete_query = """DELETE FROM dbo.rptUnosof_Customers_Dev"""

def get_url_login():
    return get_value_from_db_u(url_login_query)

def get_user_login():
    return get_value_from_db_u(user_query)

def get_pass_login():
    return get_value_from_db_u(password_query)

def get_url_cst():
    return get_value_from_db_u(url_cst_query)

def get_insert_query():
    return insert_query

def get_delete_query():
    return delete_query