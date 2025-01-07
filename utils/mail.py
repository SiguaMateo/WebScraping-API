try:
    from email.mime.text import MIMEText
    import smtplib
    import utils.data_base as data_base
except Exception as e:
    print(f"Ocurrio un error al importar las librerias en mail, {e}")

def send_mail(message):
    try:
        # Obtener datos de configuración y convertirlos explícitamente al tipo correcto
        smtp_server = str(data_base.get_server_mail())
        smtp_port = int(data_base.get_port_mail())
        user_mail = str(data_base.get_user_mail())
        pass_mail = str(data_base.get_pass_mail())
        target_mail = str(data_base.get_user_target())
        
        # Validar datos básicos
        if not smtp_server or not smtp_port:
            raise ValueError("El servidor SMTP o el puerto no están configurados correctamente.")
        
        print(f"Conectando a {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.ehlo()

        # Autenticación
        server.login(user_mail, pass_mail)

        # Crear el mensaje
        subject = "API WebScraping"
        body = f"Mensaje: {message}"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = user_mail
        msg['To'] = target_mail

        # Enviar el correo
        server.sendmail(user_mail, target_mail, msg.as_string())
        server.quit()
        print("Correo enviado exitosamente.")
    except smtplib.SMTPException as smtp_error:
        print(f"Error con el servidor SMTP: {smtp_error}")
    except ValueError as value_error:
        print(f"Error en los datos proporcionados: {value_error}")
    except Exception as e:
        message_error = f"Error con la funcion enviar correo, {e}"
        print(message_error)
        # Puedes descomentar la línea de registro en la base de datos si es necesario
        # data_base.log_to_db_f(1, "ERROR", message_error, endpoint='mail', status_code=404)
