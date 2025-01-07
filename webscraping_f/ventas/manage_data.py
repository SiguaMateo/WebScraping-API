try:
    import csv
    from datetime import datetime, timedelta
    import pandas as pd
    
    from utils.data_base import data_base_conn_f, log_to_db_f
    from utils.mail import send_mail
    from webscraping_f.ventas.data_base import get_delete_query, get_insert_query
except Exception as e:
    print("Ocurrio un error al importar las librerias en manage_data ventas, ", e)

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
        cursor.commit()
        print("Eliminación completada exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
        log_to_db_f(1, "ERROR", f"Ocurrio un error al eliminar los registros de 15 días, {e}", endpoint='delete_old_records', status_code=500)
        # send_mail(f"Ocurrio un error al eliminar los registros de 15 días, {e}")

def save():
    delete_old_records()
    try:
        with open("ventas.csv", mode="r", encoding='utf-8') as file:
            reader = list(csv.reader(file))[1:]  # Omitir la primera fila si es encabezado

            print("Inicio del proceso de inserción de datos desde el CSV")

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
                
            def clean_porcentaje(valor):
                """ Limpia el campo del porcentaje por separado para no crear conflictos con el resto de datos"""
                if pd.isna(valor) or str(valor).strip == "":
                    return None
                valor = str(valor).strip().replace("%","")
                try:
                    return float(valor)
                except ValueError:
                    return None

            for row in reader[:-1]:
                try:

                    invoice_date = clean_date(row[1])
                    
                    data = [
                        clean_text(row[0]),
                        invoice_date,
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
                        clean_text(row[13]),
                        clean_text(row[14]),
                        clean_text(row[15]),
                        clean_text(row[16]),
                        clean_text(row[17]),
                        clean_text(row[18]),
                        clean_float(row[19]),
                        clean_float(row[20]),
                        clean_float(row[21]),
                        clean_float(row[22]),
                        clean_float(row[23]),
                        clean_float(row[24]),
                        clean_float(row[25]),
                        clean_float(row[26]),
                        clean_float(row[27]),
                        clean_porcentaje(row[28])
                    ]
                    
                    # Insertar en la base de datos
                    try:
                        print(f"Insertando, {data}")
                        cursor.execute(get_insert_query(), data)
                    except Exception as db_error:
                        print(f"Error al insertar en la base de datos: {db_error}")
                        continue

                    # Confirmar cambios
                    cursor.commit()

                except Exception as e:
                    print(f"Error general en la fila: {row} - {e}")
                    continue

            print("Datos insertados desde el CSV exitosamente.")

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")