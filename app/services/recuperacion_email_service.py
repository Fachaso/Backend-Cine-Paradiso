import os
from html import escape

import requests

RESEND_API_URL = "https://api.resend.com/emails"


def enviar_correo_recuperacion(email_destino, nombre_usuario, url_recuperacion):
    api_key = os.getenv("RESEND_API_KEY")
    email_remitente = os.getenv("RESEND_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("Falta configurar RESEND_API_KEY")
    if not email_remitente:
        raise RuntimeError("Falta configurar RESEND_FROM_EMAIL")

    nombre_seguro = escape(str(nombre_usuario or "espectador"))
    url_segura = escape(str(url_recuperacion), quote=True)

    texto = "\n".join([
        f"Hola, {nombre_usuario or 'espectador'}.",
        "",
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta en Cine Paradiso.",
        "Ingresá al siguiente enlace (válido por 30 minutos):",
        url_recuperacion,
        "",
        "Si no pediste este cambio, podés ignorar este mensaje.",
    ])

    html = f"""
    <!doctype html>
    <html lang="es">
    <body style="margin:0;padding:0;background:#101010;
                font-family:Arial,Helvetica,sans-serif;color:#eeeeee">
        <table role="presentation" width="100%" cellspacing="0"
            cellpadding="0" border="0" bgcolor="#101010"
            style="width:100%;background-color:#101010">
        <tr>
            <td align="center" style="padding:24px 12px">
            <table role="presentation" width="600" cellspacing="0"
                    cellpadding="0" border="0" bgcolor="#1d1d1d"
                    style="width:100%;max-width:600px;background-color:#1d1d1d;
                            border-radius:12px;overflow:hidden">
                <tr>
                <td bgcolor="#0b0b0b"
                    style="padding:22px 28px;border-bottom:3px solid #e50920">
                    <p style="margin:0;color:#f2f2f2;font-size:20px;
                            font-weight:bold;letter-spacing:1px">
                    CINE <span style="color:#e50920">PARADISO</span>
                    </p>
                    <p style="margin:7px 0 0;color:#bdbdbd;font-size:12px;
                            letter-spacing:1px">
                    RECUPERACIÓN DE CUENTA
                    </p>
                </td>
                </tr>
                <tr>
                <td style="padding:28px">
                    <h1 style="margin:0 0 12px;color:#f2f2f2;font-size:24px;line-height:1.25">
                    Restablecé tu contraseña
                    </h1>
                    <p style="margin:0 0 16px;color:#c7c7c7;font-size:15px;line-height:1.5">
                    Hola <strong style="color:#ffffff">{nombre_seguro}</strong>, recibimos un pedido para cambiar la contraseña de tu cuenta.
                    </p>
                    <p style="margin:0 0 24px;color:#c7c7c7;font-size:14px;line-height:1.5">
                    Hacé clic en el botón de abajo para elegir una nueva contraseña. El enlace vence en <strong>30 minutos</strong>.
                    </p>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td bgcolor="#e50920" style="border-radius:8px">
                        <a href="{url_segura}"
                            style="display:inline-block;padding:13px 22px;color:#ffffff;
                                    text-decoration:none;font-weight:bold;font-size:15px">
                            Restablecer contraseña
                        </a>
                        </td>
                    </tr>
                    </table>
                    <p style="margin:24px 0 6px;color:#a7a7a7;font-size:12px">
                    Si el botón no funciona, copiá y pegá este enlace en tu navegador:
                    </p>
                    <p style="margin:0 0 20px;color:#ffaaa1;font-size:12px;word-break:break-all">
                    {escape(str(url_recuperacion))}
                    </p>
                    <p style="margin:0;color:#8e8e8e;font-size:12px">
                    Si no solicitaste este cambio, podés ignorar este correo.
                    </p>
                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
    </body>
    </html>
    """

    payload = {
        "from": email_remitente,
        "to": [email_destino],
        "subject": "Cine Paradiso - Recuperar contraseña",
        "text": texto,
        "html": html,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    respuesta = requests.post(
        RESEND_API_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()