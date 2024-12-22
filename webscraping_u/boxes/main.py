try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.select import Select
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import os
    import time
    import data_base
    import utils.mail as mail
    import utils.data_base as util_data_base
    import pandas as pd
    import re
except Exception as e:
    print(f"Error al importar las librerias en main, {e}")

def create_driver():
    """Inicializa y devuelve una instancia de ChromeDriver."""
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    # chrome_options.add_argument("--headless")  # Descomentar para ejecución en modo sin cabeza
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def login(driver):
    """Realiza el inicio de sesión en la plataforma."""
    try:
        driver.get(data_base.get_url_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(data_base.get_user())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(data_base.get_password())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Login"))).click()
        print("Inicio de sesión exitoso.")
    except Exception as e:
        error_msg = f"Error al iniciar sesión: {e}"
        util_data_base.log_to_db("ERROR", error_msg, endpoint='login', status_code=500)
        mail.send_mail(error_msg)
        raise

def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")

def clean_value(value):
    try:
        value = re.sub(r'[^\d.]', '', value.replace(' ', '').replace(',', '.'))
        if value.count('.') > 1:
            parts = value.split('.')
            value = ''.join(parts[:-1]) + '.' + parts[-1]
        return float(value)
    except ValueError:
        return 0.0

def scraple_data():
    max_retries = 5
    retries = 0
    driver = create_driver()
    login(driver)
    while retries < max_retries:
        try:
            # Obtener la fecha de hoy y hace 15 días
            today = datetime.today().date()
            start_date = datetime(2024, 11, 24).date()
            end_date = today  # Fecha final (hoy)

            print(f"Procesando datos desde {start_date} hasta {end_date}")
            driver.get(data_base.get_url_home())
            rows = []
            headers = []
            max_columns = 0

            # Convertir las fechas a string
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')

            # Navegar al sitio
            driver.get(data_base.get_url_home())

            print(f"Procesando datos desde {start_date} hasta {end_date}")

            while start_date <= end_date:  # Iterar día por día
                print(f"Extrayendo datos del día: {start_date}")
                
                # Convertir la fecha actual a string
                start_date_str = start_date.strftime('%Y-%m-%d')

                print("Fecha: ", start_date_str)

                # Acciones para el scraping del día específico
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dt_inventory_start"))).clear()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dt_inventory_start"))).send_keys(start_date_str)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dt_inventory_end"))).clear()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dt_inventory_end"))).send_keys(start_date_str)

                # Selección de otros elementos en la interfaz
                Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'nm_report')))).select_by_index(5)
                Select(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'gu_warehouse')))).select_by_index(0)

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchInventory"))).click()

                # Esperar a que los datos carguen
                WebDriverWait(driver, 120).until(EC.visibility_of_element_located((By.ID, 'tblAgedInventory')))
                print(f"Datos cargados correctamente para el día {start_date_str}")

                scroll_down(driver)

                # Extracción de datos y generación del CSV
                page_content = driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')
                table = soup.find(id='tblAgedInventory')

                if not table:
                    print(f"No se encontró la tabla en la página para el día {start_date_str}.")
                    start_date += timedelta(days=1)
                    continue

                rows = []
                headers = []
                max_columns = 0

                for j, row in enumerate(table.find_all('tr')):
                    cells = row.find_all(['td', 'th'])
                    cell_values = [cell.get_text(strip=True) for cell in cells]

                    # Cabecera
                    if j == 0:
                        headers = cell_values
                        max_columns = len(headers)
                    else:
                        # Ignorar filas no deseadas
                        if len(cell_values) == 5 and cell_values == ["PRODUCT", "TOTAL WEIGHT", "AVG WEIGHT", "BUNCHES", "STEMS"]:
                            continue
                        rows.append(cell_values)
                        max_columns = max(max_columns, len(cell_values))
                        
                # Agregar columna de fecha a cada fila
                for row in rows:
                    row.append(start_date_str)  # Fecha actual como nueva columna

                # Completar filas para alinear con el máximo de columnas
                headers.append("DATE")
                for row in rows:
                    row.extend([None] * (max_columns - len(row)))

                # Crear DataFrame y guardar datos
                df = pd.DataFrame(rows, columns=headers)
                print(df.head())
                csv_filename = f"unosof_data_1dia.csv"
                file_exists = os.path.isfile(csv_filename)
                df.to_csv(csv_filename, index=False, mode='a', header=not file_exists)
                print(f"Datos del día {start_date_str} guardados correctamente en '{csv_filename}'.")

                # Pasar al siguiente día
                start_date += timedelta(days=1)

            print("Extracción completada para todo el rango de fechas.")
            break

        except Exception as e:
            print(f"Ocurrió un error al realizar el webscraping: {e}")
            retries += 1
            time.sleep(5)

            if retries == max_retries:
                print("Límite máximo de intentos alcanzado. Finalizando.")
                break