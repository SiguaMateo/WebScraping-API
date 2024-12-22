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
    import data_base
    import utils.data_base as util_data_base
    import utils.mail as mail
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
        util_data_base.log_to_db("ERROR", error_msg, endpoint='login', status_code=500)
        mail.send_mail(error_msg)
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

            driver.get(data_base.get_url_cst())

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(data_base.get_user())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(data_base.get_password())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()

            driver.get(data_base.get_url_cst())
            
            # Esperar a que el elemento de Status esté presente
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "bo_active")))
            
            # Crear un objeto Select
            select = Select(element)

            # Seleccionar la opción con el índice 0
            select.select_by_index(0)
            
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "SearchCustomers"))).click()

            # Espera hasta que el elemento tblCustomers esté presente
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "tblCustomers")))

            scroll_down(driver)

            contenido_pagina = driver.page_source
            soup = BeautifulSoup(contenido_pagina, 'html.parser')

            rows = []
            for row in soup.find(id='tblCustomers').find_all("tr"):
                cols = row.find_all("td")
                cols = [ele.text.strip().replace("$", "").replace(",", "  ").replace('\n', '').replace('\r', '') for ele in cols]  # Limpiar texto
                if len(cols) > 0: 
                    rows.append(cols)

            if rows:
                # Crear el DataFrame con el número correcto de columnas basado en la longitud de la primera fila
                headers = [f"Column{i+1}" for i in range(len(rows[0]))]
                df = pd.DataFrame(rows, columns=headers)

                # Eliminar columnas vacías al inicio y al final
                df = df.loc[:, (df != '').any(axis=0)]
                
                # Guardar en CSV
                file_path = os.path.join(os.path.dirname(__file__), 'unosof_data_cst.csv')

                df.to_csv(file_path, header=False, index=False)
                print(f"Datos guardados correctamente en '{file_path}'.")

            else:
                print("No se encontraron filas con datos.")

            break  # Salir del bucle tras un scraping exitoso

        except Exception as e:
            retries += 1
            error_msg = f"Error al realizar el scraping: {e}"
            print(error_msg)
            util_data_base.log_to_db("ERROR", error_msg, endpoint='scraping', status_code=500)
            if retries == max_retries:
                mail.send_mail(f"Scraping fallido tras {max_retries} intentos: {e}")
        finally:
            driver.quit()  # Cerrar navegador siempre
