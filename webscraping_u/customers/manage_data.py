try:
    from webscraping_u.customers.data_base import get_delete_query, get_insert_query
    from utils.data_base import data_base_conn_u, log_to_db_u
    from utils.mail import send_mail
    import csv
except Exception as e:
    print(f"Error al importar librerías: {e}")

cursor = data_base_conn_u()

def delete_old_records():
    try:
        cursor.execute(get_delete_query())
        cursor.commit()
        print("La eliminación se completó.")
    except Exception as e:
        print(f"Error al eliminar los registros anteriores: {e}")

def clean_credit_limit(credit_limit_str):
    """
    Convierte el valor del campo 4 (crédito) a float.
    Remueve caracteres no numéricos como ';', ',' o espacios.
    """
    try:
        # Reemplazar caracteres innecesarios y convertir a float
        clean_str = credit_limit_str.replace(' ', '')
        return float(clean_str)
    except ValueError:
        print(f"Error al convertir el límite de crédito: '{credit_limit_str}'")
        return None

def save():
    delete_old_records()
    try:
        with open("unosof_data_cst.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:

                # Limpiar y convertir el campo 4 (límite de crédito) a float
                row[3] = clean_credit_limit(row[3])

                # Si la conversión falla, descartar la fila
                if row[3] is None:
                    print(f"Fila descartada por error en límite de crédito: {row}")
                    continue

                cleaned_row = [val if val != '-' else None for val in row]

                # Guardar en la base de datos
                try:
                    print("Fila insertada:, ", cleaned_row)
                    cursor.execute(get_insert_query(), cleaned_row)
                    
                except Exception as db_error:
                    print(f"Error al insertar la fila: {cleaned_row}, {db_error}")

            cursor.commit()

    except Exception as e:
        message = f"Ocurrió un error al guardar los datos en la base de datos: {e}"
        print(message)
        log_to_db_u(2, "ERROR", message, endpoint='save', status_code=404)
        # send_mail(message)
