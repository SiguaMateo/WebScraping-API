try:
    from utils.data_base import get_value_from_db_u, data_base_conn_u
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

cursor = data_base_conn_u()

# def create_table_Box():
#     with cursor:
#         # Verificar si la tabla existe y eliminarla si es así
#         cursor.execute("""
#             IF EXISTS (SELECT * FROM sysobjects WHERE name='rptCajasProducidasUnosof_Dev_Test' AND xtype='U')
#             BEGIN
#                 DROP TABLE rptCajasProducidasUnosof_Dev_Test
#             END
#         """)
#         cursor.commit()

#         # Crear una nueva tabla
#         cursor.execute("""
#             CREATE TABLE rptCajasProducidasUnosof_Dev_Test (
#             id INT PRIMARY KEY IDENTITY(1,1),
#             box_product NVARCHAR(150),
#             box_total_weight NUMERIC(10,2),
#             box_avg_weight NUMERIC(10,2),
#             box_bounches INT,
#             box_stems INT,
#             box_webscraping_date DATE
#             )
#         """)
#         cursor.commit()

# create_table_Box()

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
    return get_value_from_db_u(url_login_query)

def get_user_login():
    return get_value_from_db_u(user_query)

def get_pass_login():
    return get_value_from_db_u(password_query)

def get_url_home():
    return get_value_from_db_u(url_home_query)

def get_insert_query():
    return insert_query