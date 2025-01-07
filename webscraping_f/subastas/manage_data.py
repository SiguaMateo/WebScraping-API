try:
    import pandas as pd
    import xlrd
    from os import devnull
    from datetime import datetime, time, timedelta
    
    from utils.data_base import data_base_conn_f, log_to_db_f
    from utils.mail import send_mail
    from webscraping_f.subastas.data_base import get_insert_query, get_delete_query
except Exception as e:
    print("Ocurrió un error al importar las librerías: ", e)

cursor = data_base_conn_f()

def delete_old_records():
    try:
        # Obtener la fecha límite (hoy - 15 días)
        fecha_limite = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')

        # Obtener la consulta
        query = get_delete_query()

        # Ejecutar la consulta con el parámetro
        cursor.execute(query, (fecha_limite,))
        print(f"Registros eliminados en Ventas hasta la fecha: {fecha_limite}")

        # Confirmar cambios a través de la conexión
        cursor.commit()  # Asegúrate de usar la conexión, no el cursor.
        print("Eliminación completada exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
        log_to_db_f(2, "ERROR", f"Ocurrio un error al eliminar los registros de 15 días, {e}", endpoint='delete_old_records', status_code=500)
        # send_mail(f"Ocurrio un error al eliminar los registros de 15 días, {e}")

def save():
    delete_old_records()
    # Ruta al archivo Excel
    input_file = r"E:\API_2\WebScraping-API\webscraping_f\subastas\FloridayIoYieldExcel.xls"
    try:
        # Abrir el archivo Excel usando xlrd para evitar errores de corrupción
        wb = xlrd.open_workbook(input_file, logfile=open(devnull, 'w'), ignore_workbook_corruption=True)
        df = pd.read_excel(wb, dtype=str, skiprows=0, engine='xlrd')  # Leer el contenido del archivo .xls
        print("Archivo Excel leído correctamente. Procesando datos...")

        def clean_float(valor):
            """ Limpia y convierte un valor numérico a float. Retorna None si es vacío o no convertible. """
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            valor = str(valor).strip().replace(".", "").replace(",", ".").replace("€", "")
            try:
                return float(valor)
            except ValueError:
                return None

        def clean_text(valor):
            """ Limpia y retorna texto sin espacios innecesarios. """
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            return str(valor).strip()

        def clean_date(valor):
            """Limpia y convierte una fecha al formato '%Y-%m-%d'. Retorna None si la fecha es inválida o vacía."""
            if pd.isna(valor) or str(valor).strip() == "":
                return None
            try:
                # Indicar el formato explícito según los datos de entrada (modificar si es necesario)
                return pd.to_datetime(valor, format='%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
                try:
                    # Si falla, intenta con el formato alternativo
                    return pd.to_datetime(valor, format='%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    return None

        # Iterar sobre las filas del DataFrame
        for index, row in df.iterrows():
            try:
                # Validar la longitud de la fila
                if len(row) < 14:  # Número esperado de columnas
                    print(f"Fila inválida, columnas insuficientes: {row}")
                    continue

                # Procesar las fechas (columna 0 y 1)
                fecha_auction = clean_date(row[0])
                fecha_subasta = clean_date(row[1])

                # Construir la fila con tipos correctos
                data = [
                    fecha_auction,
                    fecha_subasta,         
                    clean_text(row[2]),
                    clean_text(row[3]),  
                    clean_text(row[4]), 
                    clean_text(row[5]),
                    clean_text(row[6]),
                    clean_text(row[7]),
                    clean_text(row[8]),
                    clean_text(row[9]),
                    clean_text(row[10]),
                    clean_text(row[11]), 
                    clean_text(row[12]),
                    clean_float(row[13]),
                    clean_float(row[14])
                ]

                # Insertar en la base de datos
                cursor.execute(get_insert_query(), tuple(data))
                print("Fila insertada:", data)

            except Exception as fila_error:
                print(f"Error en la fila: {row}, Detalle: {fila_error}")

        cursor.commit()
        print("Inserción finalizada correctamente.")

    except Exception as e:
        print(f"Ocurrió un error general: {e}")