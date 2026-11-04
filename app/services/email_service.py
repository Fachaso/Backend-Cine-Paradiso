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
        f"<li>{escape(linea)}</li>" for linea in lineas_entradas
    )
    servicios_html = ""

    if lineas_servicios:
        servicios_html = (
            "<h3>Servicios</h3><ul>"
            + "".join(
                f"<li>{escape(linea)}</li>" for linea in lineas_servicios
            )
            + "</ul>"
        )

    pelicula_html = ""
    if poster_url:
        pelicula_html = """
        <div style="text-align:center;margin:8px 0 24px">
          <img src="cid:poster_pelicula"
               alt="Póster de la película"
               width="130"
               style="display:block;width:130px;height:auto;margin:0 auto;border-radius:8px">
        </div>
        """

    titulo_html = ""
    if titulo_pelicula:
        titulo_html = (
            f'<h2 style="text-align:center;margin:0 0 20px">'
            f'{escape(titulo_pelicula)}</h2>'
        )

    html = f"""
    <html>
      <body style="margin:0;background:#f3f4f6;font-family:Arial,sans-serif;color:#172033">
        <div style="max-width:600px;margin:24px auto;background:#ffffff;border-radius:12px;overflow:hidden">
          <div style="background:#121a2b;padding:24px;color:#ffffff">
            <h1 style="margin:0;color:#ffffff">Cine Paradiso</h1>
            <p style="margin:8px 0 0;color:#d1d5db">Comprobante de compra</p>
          </div>
          <div style="padding:24px">
            <p>Gracias por tu compra.</p>
            {pelicula_html}
            {titulo_html}
            <h3>Entradas</h3>
            <ul>{entradas_html}</ul>
            {servicios_html}
            <p style="font-size:18px"><strong>Total: ${escape(total)}</strong></p>
            <div style="text-align:center;margin:24px 0">
              <p>Presentá este código QR al ingresar:</p>
              <img src="cid:qr_compra" alt="Código QR de la compra"
                   width="220" height="220">
              <p style="color:#6b7280">{escape(str(codigo_qr))}</p>
            </div>
          </div>
        </div>
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