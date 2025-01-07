try:
    import csv
    from utils.data_base import data_base_conn_u, log_to_db_u
    from utils.mail import send_mail
    from webscraping_u.boxes.data_base import get_insert_query
except Exception as e:
    print(f"Ocurrio un error al importar las liberias en manage data, {e}")

cursor = data_base_conn_u()

def save():
    try:
        with open("unosof_data_box.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                print(f"Fila leida: {row}")

                cursor.execute(get_insert_query(), row)

                cursor.commit()
            
        print(f"Datos guardados correctamente")

    except Exception as e:
        message = f"Ocurrio un error al guardar los datos en la base de datos, {e}"
        print(message)
        log_to_db_u(1, "ERROR", message, endpoint='save', status_code=404)
        # send_mail(message)
