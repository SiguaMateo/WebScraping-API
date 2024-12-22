try:
    from email.mime.text import MIMEText
    import smtplib
    import data_base
except Exception as e:
    print(f"Ocurrio un error al importar las librerias en send_mail, {e}")

def send_mail(message):
    try:
        server = smtplib.SMTP_SSL(data_base.get_server_mail(), data_base.get_port_mail())
        server.login(data_base.get_user_mail(), data_base.get_pass_mail())

        subject = "API WebScraping"
        body = f"Mensaje: {message}"

        to = data_base.get_user_target()

        msg = MIMEText(body)
        msg['Subject'] =  subject
        msg['From'] = data_base.get_user_mail()
        msg['To'] = to

        server.sendmail(data_base.get_user_mail(), to, msg.as_string())

        server.quit()
    except Exception as e:
        message_error = f"Error con la funcion enviar correo, {e}"
        print(message_error)
        data_base.log_to_db(1, "INFO", message_error, endpoint='fallido', status_code=404)

