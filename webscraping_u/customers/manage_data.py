try:
    import data_base
    import utils.data_base as util_data_base
    import utils.mail as mail
    import csv
except Exception as e:
    print(f"Error al importar librerías: {e}")

def delete_old_records():
    try:
        util_data_base.data_base_conn().execute(data_base.get_delete_query())
        util_data_base.data_base_conn().commit()
        print("La eliminación se completó.")
    except Exception as e:
        print(f"Error al eliminar los registros anteriores: {e}")

def is_valid_row(row):
    # Ignorar filas con muchos guiones
    if row.count('-') > 8:
        return False
    # Asegurarse de que la longitud de la fila sea exactamente 19
    if len(row) != 19:
        return False
    return True

def clean_credit_limit(credit_limit_str):
    """
    Convierte el valor del campo 4 (crédito) a float.
    Remueve caracteres no numéricos como ';', ',' o espacios.
    """
    try:
        # Reemplazar caracteres innecesarios y convertir a float
        clean_str = credit_limit_str.replace(',', '').replace(' ', '')
        return float(clean_str)
    except ValueError:
        print(f"Error al convertir el límite de crédito: '{credit_limit_str}'")
        return None

def save():
    delete_old_records()
    try:
        with open("unosof_data_cst.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            for row in reader:

                # Validar y limpiar la fila
                if not is_valid_row(row):
                    print(f"Fila inválida descartada: {row}")
                    continue

                # Limpiar y convertir el campo 4 (límite de crédito) a float
                row[3] = clean_credit_limit(row[3])

                # Si la conversión falla, descartar la fila
                if row[3] is None:
                    print(f"Fila descartada por error en límite de crédito: {row}")
                    continue

                cleaned_row = [val if val != '-' else None for val in row]

                # Ajustar la fila si tiene menos columnas
                while len(cleaned_row) < 19:
                    cleaned_row.append(None)

                # Guardar en la base de datos
                try:
                    util_data_base.data_base_conn().execute(data_base.get_insert_query(), cleaned_row)
                    
                except Exception as db_error:
                    print(f"Error al insertar la fila: {cleaned_row}, {db_error}")

            util_data_base.data_base_conn().commit()

    except Exception as e:
        message = f"Ocurrió un error al guardar los datos en la base de datos: {e}"
        print(message)
        util_data_base.log_to_db("ERROR", message, endpoint='fallido', status_code=404)
        mail.send_mail(message)
