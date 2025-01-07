try:
    from utils.data_base import get_value_from_db_f, data_base_conn_f
except Exception as e:
    print(f"ERROR, al importar las librerias en data_base ventas, {e}")

# def create_table_Data():
#     with data_base_conn_f() as cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='rptFresh_Portal_Ventas_Dev_Test' AND xtype='U')
#             BEGIN
#                 DROP TABLE rptFresh_Portal_Ventas_Dev_Test
#             END
#         """)
#         cursor.commit()

#        # Crear una nueva tabla con los tipos de datos ajustados
#         cursor.execute("""
#             CREATE TABLE rptFresh_Portal_Ventas_Dev_Test (
#                 id INT PRIMARY KEY IDENTITY(1,1),
#                 vent_invoice_week INT,
#                 vent_invoice_date DATE,
#                 vent_customer_group NVARCHAR(75),
#                 vent_invoice_number NVARCHAR(75),
#                 vent_customer NVARCHAR(50),
#                 vent_country_of_client NVARCHAR(50),
#                 vent_product NVARCHAR(50),
#                 vent_colour NVARCHAR(50),
#                 vent_description_allocation NVARCHAR(100),
#                 vent_weight INT, 
#                 vent_content INT,
#                 vent_customer_code NVARCHAR(20),
#                 vent_product_group NVARCHAR(50),
#                 vent_cbs_group NVARCHAR(50),
#                 vent_year_invoice_date INT,
#                 vent_month_billing_date INT,
#                 vent_day_invoice_date INT,
#                 vent_hour_invoice_date INT,
#                 vent_packaging INT,
#                 vent_total_pieces NUMERIC(10),
#                 vent_total_packages NUMERIC(10),
#                 vent_purchase NUMERIC(10, 2),
#                 vent_sale NUMERIC(10, 2), 
#                 vent_unit_price NUMERIC(10, 2), 
#                 vent_average_purchase_price NUMERIC(10, 2), 
#                 vent_comissions NUMERIC(10, 2), 
#                 vent_cost NUMERIC(10, 2), 
#                 vent_margin NUMERIC(10, 2),
#                 vent_percentage NUMERIC(10, 2)
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

insert_query = """INSERT INTO rptFresh_Portal_Ventas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

url_v_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 10 AND prm_descripcion = 'url_v'"""

delete_sales_query = """DELETE FROM rptFresh_Portal_Ventas
            WHERE vent_invoice_date > ?"""

def get_url_login():
    return get_value_from_db_f(url_login_query)

def get_user_login():
    return get_value_from_db_f(user_WSCVETS)

def get_pass_login():
    return get_value_from_db_f(password_WSCVETS)

def get_insert_query():
    return insert_query

def get_url_v():
    return get_value_from_db_f(url_v_query)

def get_delete_query():
    return delete_sales_query