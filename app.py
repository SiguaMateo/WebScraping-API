try:
    from fastapi import FastAPI
    from utils.retry import retry
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import uvicorn
    from datetime import datetime, timedelta

    from webscraping_f.ventas.main import scrape_table as ventas_scrape_table, create_driver_connection as ventas_create_driver
    from webscraping_f.ventas.manage_data import save as ventas_save
    from webscraping_f.subastas.main import get_file as subastas_get_file, create_driver_connection as subastas_create_driver
    from webscraping_f.subastas.manage_data import save as subastas_save
    from webscraping_u.boxes.main import scraple_data as boxes_scrape_data, create_driver_connection as boxes_create_driver
    from webscraping_u.boxes.manage_data import save as boxes_save
    from webscraping_u.customers.main import scrape_data as customers_scrape_data, create_driver_connection as customers_create_driver
    from webscraping_u.customers.manage_data import save as customers_save
    from webscraping_u.dae.main import scrape_data as dae_scrape_data, create_driver_connection as dae_create_driver
    from webscraping_u.dae.manage_data import save as dae_save
    from utils.data_base import data_base_conn_f, data_base_conn_u
    from utils.mail import send_mail
except ImportError as e:
    print(f"Error al importar librerías: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

app =  FastAPI(
    title="API para la obtención de datos a través de WebScraping de Starflowers Cia. Ltda.",
    description="Está API obtiene datos de páginas Web que almacenan datos de las ventas y subastas de la empresa Starflowers Cia. Ltda.",
    version="1.5.0"
)

# Diccionario para rastrear los últimos errores reportados
error_reported = {}

def should_send_mail(task_name: str, cooldown_minutes=60):
    """Determina si un correo de error debe enviarse."""
    now = datetime.now()
    if task_name in error_reported:
        last_reported = error_reported[task_name]
        if now - last_reported < timedelta(minutes=cooldown_minutes):
            # Si el último error ocurrió hace menos del cooldown, no enviar correo
            return False
    # Registrar el nuevo error y permitir envío
    error_reported[task_name] = now
    return True

@retry(max_retries=5, delay=60)
def perform_sales_scraping():
    try:
        ventas_scrape_table()
        ventas_create_driver().quit()
        ventas_create_driver().close()
        ventas_save()
    except Exception as e:
        task_name = "sales_scraping"
        if should_send_mail(task_name):
            send_mail(f"Error en ventas scraping: {e}")
        print(f"Error en ventas scraping: {e}")
    
@retry(max_retries=5, delay=60)
def perform_auctions_scraping():
    try:
        subastas_get_file()
        subastas_create_driver().quit()
        ventas_create_driver().close()
        subastas_save()
    except Exception as e:
        task_name = "sales_scraping"
        if should_send_mail(task_name):
            send_mail(f"Error en subastas scraping: {e}")
        print(f"Error en subastas scraping: {e}")

@retry(max_retries=5, delay=60)
def perform_box_scraping():
    try:
        boxes_scrape_data()
        boxes_create_driver().quit()
        boxes_create_driver().close()
        boxes_save()
    except Exception as e:
        task_name = "sales_scraping"
        if should_send_mail(task_name):
            send_mail(f"Error en cajas scraping: {e}")
        print(f"Error en cajas scraping: {e}")

@retry(max_retries=5, delay=60)
def perform_cst_scraping():
    try:
        customers_scrape_data()
        customers_create_driver().quit()
        customers_save()
    except Exception as e:
        task_name = "sales_scraping"
        if should_send_mail(task_name):
            send_mail(f"Error en clientes scraping: {e}")
        print(f"Error en clientes scraping: {e}")

@retry(max_retries=5, delay=60)
def perform_dae_scraping():
    try:
        dae_scrape_data()
        dae_create_driver().quit()
        dae_save()
    except Exception as e:
        task_name = "sales_scraping"
        if should_send_mail(task_name):
            send_mail(f"Error en dae scraping: {e}")
        print(f"Error en dae scraping: {e}")
        
def perform_all_scraping():
    try:
        perform_sales_scraping()
        print("Ventas scraping completado.")
    except Exception as e:
        print(f"Error al ejecutar el scraping de ventas: {e}")

    try:
        perform_auctions_scraping()
        print("Subastas scraping completado.")
    except Exception as e:
        print(f"Error al ejecutar el scraping de subastas: {e}")

    try:
        perform_box_scraping()
        print("Boxes scraping completado.")
    except Exception as e:
        print(f"Error al ejecutar el scraping de boxes: {e}")

    try:
        perform_cst_scraping()
        print("Clientes scraping completado.")
    except Exception as e:
        print(f"Error al ejecutar el scraping de clientes: {e}")

    try:
        perform_dae_scraping()
        print("DAE scraping completado.")
    except Exception as e:
        print(f"Error al ejecutar el scraping de DAE: {e}")
    finally:
        cursor_f = data_base_conn_f()
        cursor_u = data_base_conn_u()

@app.get("/", description="Endpoint raiz")
def default_endpoint():
    return {"message": "En ejecucion. API para WebScraping ... "}

@app.get("/get-sales", description="Endpoint para obtener las ventas")
def webscraping_sales_endpoint():
    try:
        perform_sales_scraping()
        return {"message": "Scraping realizado con éxito de las ventas"}
    except Exception as e:
        return {"Ocurrio un error al obtener los datos de las ventas ": str(e)}

@app.get("/get-auctions", description="Endpoint para obtener las subastas")
def webscraping_auctions_endpoint():
    try:
        perform_auctions_scraping()
        return {"message": "Scraping realizado con éxito de las subastas"}
    except Exception as e:
        return {f"Ocurrio un error al obtener los datos de las subastas: {str(e)}"}

@app.get("/get-u_box", description="Endpoint WebScraping")
def webscraping_box_pageu():
    try:
        perform_box_scraping()
        return {" message ": " Scraping de las cajas realizado con exito "}
    except Exception as e:
        print(f"Ocurrio un error con el Endpoint get-data-box, {e}")

@app.get("/get-u_cst")
def webscraping_cst_pageu():
    try:
        perform_cst_scraping()
        return { "message" : "Scraping de los clientes realizado con exito" }
    except Exception as e:
        print(f"ERROR, Endpoint cst, {e}")

@app.get("/get-u_dae")
def webscraping_dae_pageu():
    try:
        perform_dae_scraping()
        return { "message" : "Scraping de la data Dae realizado con exito" }
    except Exception as e:
        print(f"Ocurrio un error con dae")

def schedule_scraping_tasks():
    try:
        scheduler = BackgroundScheduler()

        # Programa la función que ejecuta todas las tareas secuencialmente
        scheduler.add_job(
            perform_all_scraping,
            CronTrigger(hour=3, minute=00),
            id='perform_all_scraping',
            replace_existing=True
        )

        # Iniciar el scheduler
        scheduler.start()
        print("Scheduler iniciado. Tareas programadas para ejecutarse secuencialmente.")
    except Exception as e:
        print(f"Ocurrió un error al programar el scheduler: {e}")


# Inicializar el scheduler al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    schedule_scraping_tasks()
    # Programa otras tareas según sea necesario

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9991)