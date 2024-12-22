try:
    import csv
    from ventas import data_base
    from datetime import datetime, timedelta
    import utils.mail as mail
    import utils.data_base as util_data_base
    import data_base
except Exception as e:
    print("Ocurrio un error al importar las librerias, ", e)

def delete_old_records():
    try:
        # Obtener la fecha límite (hoy - 15 días)
        fecha_limite = (datetime.now() - timedelta(days=15)).date()

        util_data_base.data_base_conn().execute(data_base.get_delete_query(), (fecha_limite,))
        print(f"Registros eliminados en Ventas hasta la fecha: {fecha_limite}")

        # Confirmar cambios
        util_data_base.data_base_conn().commit()
        print("Eliminación completada exitosamente.")
    except Exception as e:
        print(f"Ocurrió un error durante la eliminación de registros: {e}")
        util_data_base.log_to_db(1, "ERROR", f"Ocurrio un error al eliminar los registros de 15 días, {e}", endpoint='fallido', status_code=500)
        mail.send_mail(f"Ocurrio un error al eliminar los registros de 15 días, {e}")
        print(f"Ocurrió un error durante la eliminación de registros: {e}")

def save():
    delete_old_records()
    try:
        with open("ventas.csv", mode="r", encoding='utf-8') as file:
            reader = csv.reader(file)
            print("Inicio del proceso de inserción de datos desde el CSV")

            numeric_columns = [0, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
            negative_allowed_columns = [22, 23, 24, 25, 26, 27, 28]  # Columnas que pueden ser negativas

            for row in reader:
                try:
                    # Validar y convertir la fecha
                    fecha_str = row[1]
                    try:
                        fecha_obj = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                        row[1] = fecha_obj
                    except ValueError:
                        print(f"Error al convertir la fecha: '{fecha_str}' - Se ignorará esta fila")
                        continue

                    # Limpiar y convertir columnas numéricas
                    for col in numeric_columns:
                        try:
                            if col == 18 and row[col] == 'No packaging':
                                row[col] = 0
                            else:
                                row[col] = float(row[col].replace(',', '.'))
                        except ValueError:
                            print(f"Error al convertir columna {col}: '{row[col]}' - Se asignará 0")
                            row[col] = 0

                    # Limpiar y convertir la columna 'Weight'
                    try:
                        row[9] = int(float(row[9]))
                    except ValueError:
                        print(f"Error en la columna 'Weight': '{row[9]}' - Se asignará 0")
                        row[9] = 0

                    # Insertar en la base de datos
                    try:
                        print(f"Insertando, {row}")
                        data_base.data_base_conn().execute(data_base.get_insert_query(), row)
                    except Exception as db_error:
                        print(f"Error al insertar en la base de datos: {db_error}")
                        continue

                    # Confirmar cambios
                    data_base.data_base_conn().commit()

                except Exception as e:
                    print(f"Error general en la fila: {row} - {e}")
                    continue

            print("Datos insertados desde el CSV exitosamente.")

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")