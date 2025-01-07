try:
    from utils.data_base import get_value_from_db_u, data_base_conn_u
except Exception as e:
    print(f"ERROR, al importar las librerias, {e}")

cursor = data_base_conn_u()

# def create_table():
#     try:
#         with cursor:
#                 # Verificar si la tabla existe y eliminarla si es así
#                 cursor.execute("""
#                     IF EXISTS (SELECT * FROM sysobjects WHERE name='rptDAE_Developer_Test' AND xtype='U')
#                     BEGIN
#                         DROP TABLE rptDAE_Developer_Test
#                     END
#                 """)
#                 cursor.commit()

#                 # Crear una nueva tabla
#                 cursor.execute("""
#                     CREATE TABLE rptDAE_Developer_Test (
#                     id INT PRIMARY KEY IDENTITY(1,1),
#                     dae_mercado NVARCHAR(100),
#                     dae_semana INT,
#                     dae_partida_aduanera NVARCHAR(100),
#                     dae_descripcion_partida_adanuera NVARCHAR(100),
#                     dae_DAE NVARCHAR(20),
#                     dae_ruc_malima NVARCHAR(20),
#                     dae_exportador NVARCHAR(100),
#                     dae_cliente_billing NVARCHAR(100),
#                     dae_cliente_shipping NVARCHAR(100),
#                     dae_ruc_cliente_billing NVARCHAR(100),
#                     dae_pais_origen NVARCHAR(20),
#                     dae_pais_destino_billing NVARCHAR(30),
#                     dae_ciudad_destino_billing NVARCHAR(100),
#                     dae_direccion_billing NVARCHAR(200),
#                     dae_fecha_creacion_PO DATE,
#                     dae_fecha_vuelo NVARCHAR(20),
#                     dae_ID_PO NVARCHAR(20),
#                     dae_ID_customer_invoice NVARCHAR(20),
#                     dae_numero_factura_SRI NVARCHAR(20),
#                     dae_kg_bruto FLOAT,
#                     dae_kg_neto FLOAT,
#                     dae_udolares_FOB_kg FLOAT,
#                     dae_via NVARCHAR(20),
#                     dae_agente_carga NVARCHAR(100),
#                     dae_ciudad_embarque NVARCHAR(30),
#                     dae_valor_usd FLOAT,
#                     dae_especie NVARCHAR(200),
#                     dae_name_sku NVARCHAR(MAX),
#                     dae_cantidad_x_tipo_caja INT,
#                     dae_tipo_de_caja FLOAT,
#                     dae_tipos_de_caja_x_mercado NVARCHAR(30),
#                     dae_cajas_full FLOAT,
#                     dae_valor_credito FLOAT,
#                     dae_num_nota_credito_SRI NVARCHAR(20),
#                     dae_fecha_nota_credito_sri NVARCHAR(20),
#                     dae_unidad_medida NVARCHAR(20),
#                     dae_numero_tallos FLOAT,
#                     dae_numero_ramos FLOAT,
#                     dae_cantidad FLOAT,
#                     dae_FOB_unitario_x_tallos NVARCHAR(20),
#                     dae_FOB_total_restado_notas_credito NVARCHAR(20),
#                     dae_valor_incoterm_exportacion NVARCHAR(20),
#                     dae_incoterm_exportacion NVARCHAR(20),
#                     dae_periodo_promedio_cobro INT
#                     )
#                 """)
#                 cursor.commit()
#     except Exception as e:
#         print(f"Ocurrio un error al crear la tabla, {e}")

# create_table()


url_login_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'url_login'"""

user_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'user_name'"""

password_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 1 AND prm_descripcion = 'password'"""

url_dae_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 9 AND prm_descripcion = 'url_dae'"""

insert_query = """INSERT INTO rptDAE_Developer VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

delete_query = """DELETE FROM dbo.rptDAE_Developer
            WHERE dae_fecha_creacion_PO > ?"""

def get_url_login():
    return get_value_from_db_u(url_login_query)

def get_user_user():
    return get_value_from_db_u(user_query)

def get_pass_user():
    return get_value_from_db_u(password_query)

def get_url_dae():
    return get_value_from_db_u(url_dae_query) 

def get_insert_query():
    return insert_query

def get_delete_query():
    return delete_query