try:
    from utils.data_base import get_value_from_db_f
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

# def create_table_Data():
#     with data_base_conn_f() as cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='rptFresh_Portal_Subastas_Dev_Test' AND xtype='U')
#             BEGIN
#                 DROP TABLE rptFresh_Portal_Subastas_Dev_Test
#             END
#         """)
#         cursor.commit()

#         # Crear una nueva tabla con los tipos de datos ajustados
#         cursor.execute("""
#             CREATE TABLE rptFresh_Portal_Subastas_Dev_Test (
#                 id INT PRIMARY KEY IDENTITY(1,1),
#                 sub_auction_date DATE,
#                 sub_invoice_date DATE,
#                 sub_auction_name NVARCHAR(100),
#                 sub_buyer_name NVARCHAR(100),
#                 sub_letter NVARCHAR(100),
#                 sub_type NVARCHAR(100),
#                 sub_packaging_code INT,
#                 sub_instrument NVARCHAR(25),
#                 sub_product NVARCHAR(200),
#                 sub_weight INT,
#                 sub_quantity INT,
#                 sub_content INT,
#                 sub_total_stems INT,
#                 sub_price FLOAT,
#                 sub_sub_total FLOAT
#             )
#         """)
#         cursor.commit()
#         print("Tabla creada exitosamente.")

# create_table_Data()

url_login_query = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'url_login'"""

user_WSCVETS = """SELECT prm_valor 
                    FROM dbo.Parametros_Sistema
                    WHERE id_grupo = 1 AND prm_descripcion LIKE 'user_name'"""

password_WSCVETS = """SELECT prm_valor 
                        FROM dbo.Parametros_Sistema
                        WHERE id_grupo = 1 AND prm_descripcion LIKE 'password'"""

insert_query = """INSERT INTO rptFresh_Portal_Subastas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_s_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 13 AND prm_descripcion = 'url_s'"""
                
delete_query = """DELETE FROM rptFresh_Portal_Subastas
            WHERE sub_invoice_date > ?"""
    
def get_url_login():
    return get_value_from_db_f(url_login_query)

def get_user_login():
    return get_value_from_db_f(user_WSCVETS)

def get_pass_login():
    return get_value_from_db_f(password_WSCVETS)

def get_url_s():
    return get_value_from_db_f(url_s_query)

def get_insert_query():
    return insert_query

def get_delete_query():
    return delete_query