def email_template(subject: str, body: str, to: str):
    """
    Genera un template de email HTML para ser enviado por SMTP.

    #### Args:
        subject: str -> Asunto del email.
        body: str -> Cuerpo del email.
        to: str -> Destinatario del email.

    #### Returns:
        str: Template de email HTML.
    """
    return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8" />
        <title>{subject}</title>
        </head>
        <body style="margin:0; padding:0; background-color:#f5f5f5 !important; font-family: Arial, Helvetica, sans-serif;">

        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f5 !important; padding:20px 0;">
            <tr>
            <td align="center">

                <!-- Contenedor -->
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff !important; border-radius:6px; padding:24px;">
                
                <!-- Header -->
                <tr>
                    <td style="font-size:20px; font-weight:bold; padding-bottom:16px;">
                    <img src="https://storage.googleapis.com/darp4-storage/branding/logo-dark-2.png" alt="Darp4"/>
                    </td>
                </tr>

                <!-- Body -->
                <tr>
                    <td style="font-size:16px; line-height:1.6; color:#333333 !important;">
                    {body}
                    </td>
                </tr>

                <!-- Divider -->
                <tr>
                    <td style="padding:24px 0 !important;">
                    <hr style="border:none; border-top:1px solid #e0e0e0 !important;" />
                    </td>
                </tr>

                <!-- Footer -->
                <tr>
                    <td style="font-size:12px; color:#777777; line-height:1.5 !important;">
                    Este correo fue enviado a <strong>{to}</strong> porque tiene una relación comercial con Darp4.
                    <br /><br />

                    Si no deseas recibir más correos de este tipo, puedes
                    <a href="https://darp4.com/unsubscribe" style="color:#555555 !important;">
                        darte de baja aquí
                    </a>.
                    <br /><br />

                    © 2026 | Darp4. Todos los derechos reservados.<br />
                    Cartagena, Colombia
                    </td>
                </tr>

                </table>

            </td>
            </tr>
        </table>

        </body>
        </html>
    """