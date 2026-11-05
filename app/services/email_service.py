import base64
import os
from html import escape

import requests

from app.utils.qr_generator import generar_qr_png


RESEND_API_URL = "https://api.resend.com/emails"


def _texto(valor):
    return "-" if valor is None else str(valor)


def _linea_entrada(entrada):
    fila = _texto(entrada.get("fila"))
    numero = _texto(entrada.get("numero"))
    butaca = f"{fila}{numero}" if fila != "-" or numero != "-" else _texto(
        entrada.get("id_asiento")
    )
    precio = _texto(entrada.get("precio"))
    return f"Butaca {butaca} - ${precio}"


def _linea_servicio(servicio):
    nombre = servicio.get("nombre_servicio") or servicio.get("nombre")
    cantidad = _texto(servicio.get("cantidad"))
    precio = _texto(servicio.get("precio_unitario", servicio.get("precio")))
    return f"{_texto(nombre)} x{cantidad} - ${precio} c/u"


def _armar_contenido(datos_compra):
    entradas = datos_compra.get("entradas", [])
    servicios = datos_compra.get("servicios", [])
    pelicula = datos_compra.get("pelicula") or {}

    titulo_pelicula = pelicula.get("titulo_pelicula")
    poster_url = (pelicula.get("poster_url") or "").strip()
    if not poster_url.startswith("https://"):
        poster_url = ""

    compra = datos_compra["compra"]
    total = _texto(compra.get("monto_total"))
    codigo_qr = compra.get("codigo_qr")
    id_compra = _texto(compra.get("id_compra"))

    if not codigo_qr:
        raise ValueError("La compra no tiene codigo_qr")

    lineas_entradas = [_linea_entrada(e) for e in entradas]
    lineas_servicios = [_linea_servicio(s) for s in servicios]

    texto = ["Gracias por tu compra en Cine Paradiso."]
    if titulo_pelicula:
        texto.append(f"Película: {titulo_pelicula}")

    texto += [
        "",
        "Entradas:",
        *[f"- {linea}" for linea in lineas_entradas],
    ]

    if lineas_servicios:
        texto += ["", "Servicios:", *[f"- {linea}" for linea in lineas_servicios]]

    texto += [
        "",
        f"Total: ${total}",
        f"Código QR: {codigo_qr}",
        "Presentá el QR al ingresar.",
    ]

    entradas_html = "".join(
        f"""
        <tr>
        <td style="padding:12px 14px;background:#292929;
                    border-bottom:1px solid #3a3a3a;color:#eeeeee;
                    font-size:14px">
            {escape(linea)}
        </td>
        </tr>
        """
        for linea in lineas_entradas
    )

    servicios_html = ""
    if lineas_servicios:
        servicios_rows = "".join(
            f"""
            <tr>
            <td style="padding:12px 14px;background:#292929;
                        border-bottom:1px solid #3a3a3a;color:#eeeeee;
                        font-size:14px">
                {escape(linea)}
            </td>
            </tr>
            """
            for linea in lineas_servicios
        )
        servicios_html = f"""
        <tr>
        <td style="padding:0 28px 22px">
            <h3 style="margin:0 0 10px;color:#ffaaa1;font-size:15px">
            Servicios
            </h3>
            <table role="presentation" width="100%" cellspacing="0"
                cellpadding="0" border="0">
            {servicios_rows}
            </table>
        </td>
        </tr>
        """

    pelicula_html = ""
    if poster_url:
        pelicula_html = """
        <table role="presentation" width="100%" cellspacing="0"
            cellpadding="0" border="0">
        <tr>
            <td align="center" style="padding:8px 0 16px">
            <img src="cid:poster_pelicula"
                alt="Póster de la película"
                width="145"
                style="display:block;width:145px;max-width:100%;
                        height:auto;margin:0 auto;border-radius:8px;
                        border:1px solid #3a3a3a">
            </td>
        </tr>
        </table>
        """

    titulo_html = ""
    if titulo_pelicula:
        titulo_html = (
            f'<h2 style="margin:0 0 22px;text-align:center;'
            f'color:#f2f2f2;font-size:24px;line-height:1.3">'
            f'{escape(titulo_pelicula)}</h2>'
        )

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
                    TU PRÓXIMA FUNCIÓN
                    </p>
                </td>
                </tr>

                <tr>
                <td style="padding:26px 28px 8px">
                    <span style="display:inline-block;padding:7px 11px;
                                background-color:#e50920;color:#ffffff;
                                border-radius:5px;font-size:11px;
                                font-weight:bold;letter-spacing:1px">
                    COMPRA CONFIRMADA
                    </span>
                    <h1 style="margin:17px 0 8px;color:#f2f2f2;
                            font-size:25px;line-height:1.25">
                    Tu entrada está lista
                    </h1>
                    <p style="margin:0;color:#c7c7c7;font-size:15px;
                            line-height:1.5">
                    Gracias por elegir Cine Paradiso. Acá tenés los datos
                    de tu compra y el QR para ingresar.
                    </p>
                </td>
                </tr>

                <tr>
                <td style="padding:14px 28px 4px">
                    {pelicula_html}
                    {titulo_html}
                </td>
                </tr>

                <tr>
                <td style="padding:0 28px 22px">
                    <h3 style="margin:0 0 10px;color:#ffaaa1;font-size:15px">
                    Entradas
                    </h3>
                    <table role="presentation" width="100%" cellspacing="0"
                        cellpadding="0" border="0">
                    {entradas_html}
                    </table>
                </td>
                </tr>

                {servicios_html}

                <tr>
                <td style="padding:0 28px 24px">
                    <table role="presentation" width="100%" cellspacing="0"
                        cellpadding="0" border="0" bgcolor="#2a2020"
                        style="background-color:#2a2020;
                                border-left:4px solid #e50920">
                    <tr>
                        <td style="padding:14px;color:#c7c7c7;font-size:14px">
                        TOTAL
                        </td>
                        <td align="right"
                            style="padding:14px;color:#ffffff;
                                font-size:20px;font-weight:bold">
                        ${escape(total)}
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>

                <tr>
                <td align="center" style="padding:0 28px 28px">
                    <p style="margin:0 0 14px;color:#f2f2f2;font-size:15px">
                    Presentá este QR al ingresar
                    </p>
                    <table role="presentation" cellspacing="0" cellpadding="0"
                        border="0" bgcolor="#ffffff"
                        style="background-color:#ffffff;border-radius:12px">
                    <tr>
                        <td style="padding:14px">
                        <img src="cid:qr_compra"
                            alt="Código QR de la compra"
                            width="220" height="220"
                            style="display:block;width:220px;height:220px">
                        </td>
                    </tr>
                    </table>
                    <p style="margin:12px 0 0;color:#a7a7a7;font-size:12px">
                    Código: {escape(str(codigo_qr))}
                    </p>
                </td>
                </tr>

                <tr>
                <td align="center" bgcolor="#141414"
                    style="padding:18px 28px;background-color:#141414;
                            border-top:1px solid #303030">
                    <p style="margin:0;color:#a7a7a7;font-size:12px">
                    Cine Paradiso · Gracias por venir
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

    return "\n".join(texto), html, str(codigo_qr), id_compra, poster_url


def enviar_comprobante_compra(email_destino, datos_compra):
    api_key = os.getenv("RESEND_API_KEY")
    email_remitente = os.getenv("RESEND_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("Falta configurar RESEND_API_KEY")
    if not email_remitente:
        raise RuntimeError("Falta configurar RESEND_FROM_EMAIL")

    texto, html, codigo_qr, id_compra, poster_url = _armar_contenido(
        datos_compra
    )

    qr_base64 = base64.b64encode(generar_qr_png(codigo_qr)).decode("ascii")

    adjuntos = [
        {
            "filename": "codigo-qr.png",
            "content": qr_base64,
            "content_id": "qr_compra",
        }
    ]

    if poster_url:
        adjuntos.append({
            "filename": "poster-pelicula.jpg",
            "path": poster_url,
            "content_id": "poster_pelicula",
        })

    payload = {
        "from": email_remitente,
        "to": [email_destino],
        "subject": "Cine Paradiso - Confirmación de compra",
        "text": texto,
        "html": html,
        "attachments": adjuntos,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Se conserva internamente para evitar correos duplicados.
        "Idempotency-Key": f"compra-confirmada/{id_compra}",
    }

    respuesta = requests.post(
        RESEND_API_URL,
        headers=headers,
        json=payload,
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()