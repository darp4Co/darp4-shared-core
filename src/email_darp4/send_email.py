import smtplib
import ssl
from email.message import EmailMessage
import logging
from dotenv import load_dotenv
import os
from .template import email_template

load_dotenv()

logger = logging.getLogger(__name__)


async def send_email_smtp(from_email: str, to: str, subject: str, body: str, from_name: str | None = None, reply_to: str | None = None):
    """
    Envía un email utilizando SMTP.

    #### Args:
        from_email: str -> Email de origen.
        to: str -> Email de destino.
        subject: str -> Asunto del email.
        body: str -> Cuerpo del email.
        from_name: str | None -> Nombre de la persona que envía el email.
        reply_to: str | None -> Email de respuesta.

    #### Returns:
        None

    #### Raises:
        Exception: Si ocurre un error al enviar el email.
    """
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    html_body = email_template(subject, body, to)
    msg = EmailMessage()
    msg.set_content("Si no deseas recibir más correos, visita: https://darp4.com/unsubscribe")
    msg.add_alternative(html_body, subtype='html')
    msg['Subject'] = subject
    if from_name:
        msg['From'] = f"{from_name} <{from_email}>"
    else:
        msg['From'] = from_email
    msg['To'] = to
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["List-Unsubscribe"] = "<https://darp4.com/unsubscribe>"

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT), context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        raise e
