try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup
    import pandas as pd
    import data_base
    import utils.data_base as util_data_base
    import utils.mail as mail
    from datetime import datetime, time, timedelta
    import time
    print("Librerias Importadas")
except Exception as e:
    print("Error al importar las librerias en ventas, ", e)

def create_driver_connection():
    options = Options()
    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
    options.add_argument("--headless") # visualizar el navegador
    options.binary_location = brave_path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            driver.get(data_base.get_url_login())

            print("Iniciando sesion")
            # Iniciar sesión
            username = driver.find_element(By.ID, 'username')
            username.send_keys(data_base.get_User())
            password = driver.find_element(By.ID, 'password')
            password.send_keys(data_base.get_Pass())

            message = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.fps-button'))).click()
            print(message)
            break

        except Exception as e:
            retries += 1
            print("Ocurrio un error al iniciar sesion, ", e)
            time.sleep(20)
            
            if retries < max_retries:
                driver.refresh()  # Recargar la página para reintentar
                time.sleep(10)
            
            elif retries == max_retries:
                util_data_base.log_to_db(2, "ERROR", f"Ocurrio un error al iniciar sesión, {e}", endpoint='fallido', status_code=500)
                mail.send_mail(f"Ocurrio un error al inciar sesión, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()

def clean_value(value):
    """
    Limpia y convierte un valor numérico con formato europeo a formato estándar.
    """
    try:
        # Eliminar separadores de miles y convertir a formato de punto decimal
        value = value.replace('.', '').replace(',', '.')
        return float(value)
    except Exception as e:
        print(f"Error al limpiar valor: '{value}', {e}")
        return None

def generate_url_base(start, end):
    base_url = data_base.get_url_v()
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

def scrape_table():
    driver = create_driver_connection()
    login(driver)
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            url = generate_url()
            driver.get(url)

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "management_total_table"))
            )

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            table = soup.find(id='management_total_table')

            if not table:
                print("No se encontró la tabla en la página.")
                raise ValueError("Tabla no encontrada.")

            rows = []
            max_columns = 0

            # Procesar las filas de la tabla
            for j, row in enumerate(table.find_all('tr')):
                cells = row.find_all(['td', 'th'])
                cell_values = [cell.get_text(strip=True) for cell in cells]

                if j == 0:  # Primera fila son los encabezados
                    headers = cell_values
                    max_columns = len(headers)
                else:
                    max_columns = max(max_columns, len(cell_values))
                    rows.append(cell_values)

            # Ajustar encabezados y filas al mismo tamaño
            headers += [None] * (max_columns - len(headers))
            rows = [row + [None] * (max_columns - len(row)) for row in rows]

            # Crear el DataFrame
            df = pd.DataFrame(rows, columns=headers)

            csv_filename = "ventas.csv"
            df.to_csv(csv_filename, index=False)
            # print(f"Datos guardados como '{csv_filename}'")

            break

        except Exception as e:
            retries += 1
            time.sleep(15)
            print("Ocurrio un error al encontrar y extraer los datos de la tabla, ", e)
            if retries == max_retries:
                util_data_base.log_to_db(1, "ERROR", f"Ocurrio un error al extraer los datos de la página web, {e}", endpoint='fallido', status_code=500)
                mail.send_mail(f"Ocurrio un error al extraer los datos de la página web, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()
                driver.close()