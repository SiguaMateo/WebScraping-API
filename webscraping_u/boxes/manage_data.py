try:
    import csv
    import utils.data_base as util_data_base
    import utils.mail as mail
    import data_base
except Exception as e:
    print(f"Ocurrio un error al importar las liberias en manage data, {e}")

def save():
    try:
        with open("unosof_data_1dia.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)

            for row in reader:
                print("Ingreso al bucle")
                print(f"Fila leida: {row}")

                util_data_base.data_base_conn().execute(data_base.get_insert_query(), row)
                print(f"Datos guardados correctamente")

                util_data_base.data_base_conn().commit()        

    except Exception as e:
        message = f"Ocurrio un error al guardar los datos en la base de datos, {e}"
        print(message)
        data_base.log_to_db(1, "ERROR", message, endpoint='fallido', status_code=404)
        mail.send_mail(message)
