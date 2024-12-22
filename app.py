try:
    from fastapi import FastAPI
    import webscraping_f.ventas.main as main_file_ventas
    import webscraping_f.ventas.manage_data as manage_data_ventas
    import webscraping_f.subastas.main as main_file_subastas
    import webscraping_f.subastas.manage_data as manage_data_subastas
    import webscraping_u.boxes.main as main_box
    import webscraping_u.boxes.manage_data as manage_data_box
    import webscraping_u.customers.main as main_cst
    import webscraping_u.customers.manage_data as manage_data_cst
    import webscraping_u.dae.main as main_dae
    import webscraping_u.dae.manage_data as manage_data_dae
    from utils.retry import retry
    from utils.scheduler import start_scheduler, schedule_daily_task
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import asyncio
    import uvicorn
except ImportError as e:
    print(f"Error al importar librerías: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

app =  FastAPI(
    title="API para la obtención de datos a través de WebScraping de Starflowers Cia. Ltda.",
    description="Está API obtiene datos de páginas Web que almacenan datos de las ventas y subastas de la empresa Starflowers Cia. Ltda.",
    version="1.0.0"
)

@retry(max_retries=5, delay=2)
def perform_sales_scraping():
    main_file_ventas.scrape_table()
    main_file_ventas.create_driver_connection().quit()
    manage_data_ventas.save()
    
@retry(max_retries=5, delay=2)
def perform_auctions_scraping():
    main_file_subastas.get_file()
    main_file_subastas.create_driver_connection().quit()
    manage_data_subastas.save()

@retry(max_retries=5, delay=2)
def perform_box_scraping():
    main_box.scraple_data()
    main_box.create_driver().quit()
    manage_data_box.save()

@retry(max_retries=5, delay=2)
def perform_cst_scraping():
    main_cst.scrape_data()
    main_cst.create_driver().quit()
    manage_data_cst.save()

@retry(max_retries=5, delay=2)
def perform_dae_scraping():
    main_dae.scrape_data()
    main_dae.create_driver().quit()
    manage_data_dae.save()

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
        return {" message ": " Obteniendo datos "}
    except Exception as e:
        print(f"Ocurrio un error con el Endpoint get-data-box, {e}")

@app.get("")
def webscraping_cst_pageu():
    try:
        perform_cst_scraping()
    except Exception as e:
        print(f"ERROR, Endpoint cst, {e}")

@app.get("/get-u_dae")
def webscraping_dae_pageu():
    try:
        perform_dae_scraping()
    except Exception as e:
        print(f"Ocurrio un error con dae")

# Función para programar las tareas
def schedule_scraping_tasks():
    try:
        scheduler = BackgroundScheduler()

        # Programar el scraping de ventas todos los días a las 8 PM
        scheduler.add_job(
            webscraping_sales_endpoint,
            CronTrigger(hour=23, minute=00),
            id='scrape_sales',
            replace_existing=True
        )

        # Programar el scraping de subastas todos los días a las 8:05 PM
        scheduler.add_job(
            webscraping_auctions_endpoint,
            CronTrigger(hour=23, minute=00),
            id='scrape_auctions',
            replace_existing=True
        )

        # Iniciar el scheduler
        scheduler.start()
        print("Scheduler iniciado. Tareas programadas.")
    except Exception as e:
        print(f"Ocurrio un error en el evento programado, ", e)

# Inicializar el scheduler al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    scheduler = start_scheduler()
    schedule_daily_task(scheduler, perform_sales_scraping, hour=3, minute=0, id='scrape_sales')
    # Programa otras tareas según sea necesario

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=9991)