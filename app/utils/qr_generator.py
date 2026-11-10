import io

import qrcode


def generar_qr_png(codigo_qr):
    """Devuelve los bytes de una imagen PNG con el QR del código."""
    imagen = qrcode.make(codigo_qr)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()