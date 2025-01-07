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
    import pandas as pd
    import os
    
    from webscraping_u.customers.data_base import get_url_login, get_user_login, get_pass_login, get_url_cst
    from utils.data_base import log_to_db_u, data_base_conn_u
    from utils.mail import send_mail
except Exception as e:
    print(f"Error al importar las librerías en main cst: {e}")
    raise

def create_driver_connection():
    options = Options()
    brave_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    options.add_argument("--headless") # No visualizar el navegador
    options.binary_location = brave_path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    """Realiza el inicio de sesión en la plataforma."""
    try:
        driver.get(get_url_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_pass_login())
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "Login"))).click()
        print("Inicio de sesión exitoso.")
    except Exception as e:
        error_msg = f"Error al iniciar sesión: {e}"
        log_to_db_u(2, "ERROR", error_msg, endpoint='login', status_code=500)
        # send_mail(error_msg)
        raise

def scroll_down(driver):
    """Desplaza la página hacia abajo."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    WebDriverWait(driver, 2).until(lambda d: d.execute_script("return document.readyState") == "complete")

def scrape_data():
    """Realiza el web scraping de los reportes."""
    max_retries = 3
    retries = 0
    driver = create_driver_connection()  # Crear instancia del navegador
    login(driver)

    while retries < max_retries:
        try:

            driver.get(get_url_cst())

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(get_user_login())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(get_pass_login())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Login"))).click()

            driver.get(get_url_cst())
            
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
                df = pd.DataFrame(rows)

                # Eliminar columnas vacías al inicio y al final
                df = df.loc[:, (df != '').any(axis=0)]
                
                csv_filename = f"unosof_data_cst.csv"
                df.to_csv(csv_filename, index=False)

            else:
                print("No se encontraron filas con datos.")

            break  # Salir del bucle tras un scraping exitoso

        except Exception as e:
            retries += 1
            error_msg = f"Error al realizar el scraping: {e}"
            print(error_msg)
            log_to_db_u("ERROR", error_msg, endpoint='scrape_data', status_code=500)
            if retries == max_retries:
                print()
                # send_mail(f"Scraping fallido tras {max_retries} intentos: {e}")
        finally:
            driver.quit()  # Cerrar navegador siempre
        try:
            driver.close()
            driver.quit()
            print("Conexiones cerradas")
        except Exception as e:
            print(f"ERROR al cerrar las conexiones, {e}")