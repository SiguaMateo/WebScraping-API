from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, time, timedelta
import pandas as pd
import time
from webscraping_f.ventas.data_base import get_url_login, get_user_login, get_pass_login, get_url_v
from utils.data_base import log_to_db_f
from utils.mail import send_mail
print("Librerias Importadas")

def create_driver_connection():
    options = Options()
    # Si deseas usar Chrome en lugar de Brave, ajusta la ruta de binary_location
    options.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    options.add_argument("--headless") # No visualizar el navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # No especificar la versión
    return driver


def login(driver):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            driver.get(get_url_login())

            print("Iniciando sesion")
            # Iniciar sesión
            username = driver.find_element(By.ID, 'username')
            username.send_keys(get_user_login())
            password = driver.find_element(By.ID, 'password')
            password.send_keys(get_pass_login())

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
                log_to_db_f(1, "ERROR", f"Ocurrio un error al iniciar sesión, {e}", endpoint='login', status_code=500)
                # send_mail(f"Ocurrio un error al inciar sesión, {e}")
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
    base_url = get_url_v()
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

            break

        except Exception as e:
            retries += 1
            time.sleep(15)
            print("Ocurrio un error al encontrar y extraer los datos de la tabla, ", e)
            if retries == max_retries:
                log_to_db_f(1, "ERROR", f"Ocurrio un error al extraer los datos de la página web, {e}", endpoint='scrape_table', status_code=500)
                # send_mail(f"Ocurrio un error al extraer los datos de la página web, {e}")
                raise
        finally:
            if retries == max_retries:
                driver.quit()
                driver.close()
        
        try:
            driver.close()
            driver.quit()
            print("Conexiones cerradas")
        except Exception as e:
            print(f"ERROR al cerrar las conexiones, {e}")