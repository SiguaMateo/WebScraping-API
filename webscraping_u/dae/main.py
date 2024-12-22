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
    import utils.data_base as util_data_base
    import utils.mail as send_mail
    import data_base
    import pandas as pd
    import os
except Exception as e:
    print(f"Error al importar las librerías: {e}")
    raise

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
        util_data_base.log_to_db(1, "ERROR", error_msg, endpoint='login', status_code=500)
        send_mail.send_mail(error_msg)
        raise

def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")

def scrape_data():
    """Realiza el web scraping de los reportes."""
    max_retries = 3
    retries = 0

    while retries < max_retries:
        driver = create_driver()  # Crear instancia del navegador
        try:
            login(driver)

            # Configurar rango de fechas
            start_date = datetime(2022, 10, 26)  # Fecha de inicio
            end_date = datetime.today()  # Fecha de hoy

            driver.get(data_base.get_url_dae())

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(data_base.get_user())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(data_base.get_password())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()

            driver.get(data_base.get_url_dae())

            while start_date <= end_date:
                print(f"Extrayendo datos del rango de fechas: {start_date} a {start_date + timedelta(days=14)}")
                
                # Convertir las fechas de inicio y fin a strings
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = (start_date + timedelta(days=14)).strftime('%Y-%m-%d')

                # Rellenar el formulario con las fechas
                fechaInicio = driver.find_element(By.NAME, 'dt_search_start_1')
                fechaInicio.clear()
                fechaInicio.send_keys(start_date_str)
                fechaFin = driver.find_element(By.NAME, 'dt_search_end_1')
                fechaFin.clear()
                fechaFin.send_keys(end_date_str)

                # Configurar filtros
                Select(driver.find_element(By.ID, 'dt_filter_1')).select_by_index(2)
                Select(driver.find_element(By.ID, 'reportID1')).select_by_index(26)
                driver.find_element(By.NAME, 'GenerateReport_1').click()

                # Esperar carga del reporte
                WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "tblAWBDetail")))

                # Extraer datos
                scroll_down(driver)
                contenidoPagina = driver.page_source
                soup = BeautifulSoup(contenidoPagina, "html.parser")

                rows = []
                for a in soup.find(id='tblAWBDetail').find_all("td", {"class": "noclass"}):
                    rows.append(a.text)

                rango = len(rows) // 44  # Calcular cuántas filas de datos hay

                # Definir las cabeceras de las columnas
                headers = [f"Column{i+1}" for i in range(44)]  # Personalizar según el contenido

                rows_data = []
                for x in range(int(rango)):
                    row = rows[x * 44:(x + 1) * 44]
                    if len(row) == 44:  # Verificar que la fila tiene el número correcto de columnas
                        # Limpiar las celdas
                        row = [cell.replace('\n', ' ').strip() for cell in row]

                        # Unir direcciones fragmentadas si es necesario
                        if len(row[12].split()) > 2:  # Verificar si es una dirección fragmentada
                            row[12] = " ".join(row[12].split())
                            
                        # Procesar la fecha (columna 14)
                        try:
                            dateTimeObj = datetime.strptime(row[14], '%b-%d-%Y')
                            row[14] = dateTimeObj
                        except Exception as e:
                            print(f"Error al convertir la fecha: {e}")
                            row[14] = None

                        # Añadir la fila a los datos
                        rows_data.append(row)
                    else:
                        print(f"Fila omitida debido a un número incorrecto de columnas: {len(row)}")

                # Crear DataFrame y guardar los datos
                if rows_data:
                    df = pd.DataFrame(rows_data, columns=headers)
                    file_path = os.path.join(os.path.dirname(__file__), 'unosof_data.csv')

                    # Si el archivo ya existe, añadir los datos a continuación
                    if os.path.exists(file_path):
                        df.to_csv(file_path, mode='a', header=False, index=False)
                    else:
                        df.to_csv(file_path, index=False)
                    print(f"Datos guardados correctamente en '{file_path}'.")

                else:
                    print("No se encontraron filas con el número esperado de columnas.")

                # Actualizar la fecha de inicio para la próxima iteración (15 días después)
                start_date += timedelta(days=15)

            break

        except Exception as e:
            retries += 1
            error_msg = f"Error al realizar el scraping: {e}"
            print(error_msg)
            util_data_base.log_to_db(1, "ERROR", error_msg, endpoint='scraping', status_code=500)
            if retries == max_retries:
                send_mail.send_mail(f"Scraping fallido tras {max_retries} intentos: {e}")
        finally:
            driver.quit()  # Cerrar navegador siempre