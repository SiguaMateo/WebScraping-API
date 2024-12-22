try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from datetime import datetime, time, timedelta
    import time
    import os
    import pandas as pd
    import utils.mail as send_email
    import utils.data_base as util_data_base
    import data_base
except Exception as e:
    print("Ocurrió un error al importar las librerías en subastas main", e)

def create_driver_connection():
    # Inicializar el navegador
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"

    # Establecer la carpeta de descargas
    prefs = {
        "download.default_directory": os.path.expanduser('~/Escritorio/Starflowers/API/API-WebScraping/subastas'),
        "download.prompt_for_download": False,  # No preguntar al usuario
        "download.directory_upgrade": True,    # Permitir actualizaciones del directorio de descargas
        "safebrowsing.enabled": True           # Permitir descargas seguras
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Inicializar el navegador con las opciones configuradas
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login(driver):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:

            driver.get(data_base.get_url_login())
            # Iniciar sesión
            username = driver.find_element(By.ID, 'username')
            username.send_keys(data_base.get_url_login())
            password = driver.find_element(By.ID, 'password')
            password.send_keys(data_base.get_pass_mail())

            message = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fps-button'))).click()
            print(message)
            break

        except Exception as e:
            retries += 1
            print("Ocurrio un error al iniciar sesion, ", e)
            time.sleep(3)
            if retries == max_retries:
                util_data_base.log_to_db(2, "ERROR", f"Ocurrio un error al iniciar sesión, {e}", endpoint='fallido', status_code=500)
                send_email.send_mail(f"Ocurrio un error al inciar sesión, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()

def delete_file():
    # Ruta del archivo que deseas eliminar
    file_path = "~/Escritorio/Starflowers/API/API-WebScraping/subastas/FloridayIoYieldExcel.xls"

    try:
        # Verifica si el archivo existe
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"El archivo {file_path} ha sido eliminado correctamente.")
        else:
            print(f"El archivo {file_path} no existe.")
    except Exception as e:
        print(f"Ocurrió un error al intentar eliminar el archivo: {e}")

def wait_table(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ajax_table_table tbody"))
        )
        print("Tabla cargada correctamente")
    except Exception as e:
        print("Error al cargar la tabla:", e)
        driver.quit()

def wait_for_download(download_dir, timeout=30):
    end_time = time.time() + timeout
    while time.time() < end_time:
        files = os.listdir(download_dir)
        # Verifica si hay un archivo con extensión .xls o .xlsx
        if any(file.endswith((".xls", ".xlsx")) for file in files):
            return True
        time.sleep(1)
    raise Exception("El archivo no se descargó en el tiempo esperado")

def process_downloaded_file(download_dir):
    files = [f for f in os.listdir(download_dir) if f.endswith((".xls", ".xlsx"))]
    if not files:
        raise Exception("No se encontró ningún archivo descargado")
    
    file_path = os.path.join(download_dir, files[0])
    time.sleep(5)
    # Validar manualmente el archivo descargado
    try:
        print(f"Procesando archivo: {file_path}")
        with open("FloridayIoYieldExcel.xls", "rb") as f:
            print(f.read(512))  # Inspecciona los primeros bytes del archivo
            header = f.read(8)
            print(f"Cabecera del archivo: {header}")
            if b'<?xml' in header or b'PK' in header:
                print("El archivo parece ser un .xlsx válido.")
            elif b'\xD0\xCF\x11\xE0' in header:
                print("El archivo parece ser un .xls válido.")
            else:
                raise Exception("El archivo no parece ser un formato Excel válido.")
    except Exception as e:
        print(f"Error validando el archivo: {e}")
        return

    # Leer el archivo Excel
    try:
        data = pd.read_excel("FloridayIoYieldExcel.xls", engine="xlrd")
        print("Datos del archivo descargado:")
        print(data.head())  # Verificar los primeros registros

        # Guardar en un archivo CSV
        csv_path = os.path.join(download_dir, "data.csv")
        data.to_csv(csv_path, index=False)
        print(f"Datos guardados en {csv_path}")

        # Eliminar el archivo original si ya no lo necesitas
        os.remove(file_path)
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")

download_dir = os.path.expanduser('~/Escritorio/Starflowers/API/API-WebScraping/subastas')

def generate_url_base(start, end):
    base_url = data_base.get_url_y()
    print(f"URL_BASE: ", base_url)
    if not base_url:
        raise ValueError("La base URL obtenida de la base de datos es inválida.")
    return base_url.format(start_date=start, end_date=end)

def generate_url():
    try:
        today = datetime.today().date()
        start_date = (today - timedelta(days=15)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        url = generate_url_base(start_date, end_date)
        print(f"URL valida: ", url)
        if not url:
            raise ValueError("La URL generada es inválida o está vacía.")
        return url
    except Exception as e:
        print(f"ERROR, al generar la fecha o la URL: {e}")
        # Retorna un valor por defecto para evitar el error
        return "about:blank/error"

def get_file():
    delete_file()
    driver = create_driver_connection()
    login(driver)
    url = generate_url()
    print("URL: ", url)
    driver.get(url)
    wait_table(driver)
    time.sleep(10)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'export'))
        ).click()
        time.sleep(10)
        print(f"Ingreso al primer try")
    except Exception as e:
        print(f"ERROR, ocurrió un error mientras esperaba el botón exportar: {e}")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.export_excel.btn-export"))
        ).click()
        wait_for_download(download_dir)
        process_downloaded_file(download_dir)
        print(f"Ingreso al segundo try")
        time.sleep(5)
    except Exception as e:
        print(f"ERROR, esperando el boton descargar: {e}")

    try:
        driver.close()
        driver.quit()
        data_base.cursor.close()
        print("Conexiones cerradas")
    except Exception as e:
        print(f"ERROR al cerrar las conexiones, {e}")