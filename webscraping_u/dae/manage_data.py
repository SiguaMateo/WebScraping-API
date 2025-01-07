try:
    import csv
    from datetime import datetime, timedelta
    
    from utils.data_base import data_base_conn_u, log_to_db_u
    from utils.mail import send_mail
    from webscraping_u.dae.data_base import get_delete_query, get_insert_query
except Exception as e:
    print(f"Ocurrio un error al importar las liberias en manage data, {e}")

cursor = data_base_conn_u()

def delete_old_records():
    today = datetime.now()
    date_calculate = (today - timedelta(days=15)).strftime('%Y-%m-%d')
    try:
        cursor.execute(get_delete_query(), str(date_calculate))
        cursor.commit()
        print("La eliminacion se completo ... ")
    except Exception as e:
        print(f"Error al eliminar los registros anteriores, {e}")

def save():
    delete_old_records()
    try:
        with open("unosof_data_dae.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar la cabecera

            for row in reader:
                print(f"Fila leída: {row}")

                # Limpiar las celdas
                row = [cell.replace('\n', ' ').strip() for cell in row]

                # Unir direcciones fragmentadas si es necesario
                if len(row[12].split()) > 2:  # Verificar si es una dirección fragmentada
                    row[12] = " ".join(row[12].split())

                # Procesar la fecha (columna 14)
                try:
                    dateTimeObj = datetime.strptime(row[14], '%b-%d-%Y')
                    row[14] = dateTimeObj
                except ValueError as e:
                    print(f"Error al convertir la fecha en la columna 14: {e}. Valor: {row[14]}")
                    row[14] = None

                # Guardar en la base de datos
                try:
                    cursor.execute(get_insert_query(), row)
                except Exception as db_error:
                    print(f"Error al insertar la fila en la base de datos: {db_error}")
                    continue  # Saltar a la siguiente fila

            print("Datos guardados correctamente")
            cursor.commit()

    except Exception as e:
        message = f"Ocurrió un error al guardar los datos en la base de datos: {e}"
        print(message)
        log_to_db_u(3, "ERROR", message, endpoint='save', status_code=404)
        # send_mail(message)