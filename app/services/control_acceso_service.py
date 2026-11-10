from app.repositories.compra_repository import validar_qr


def usar_codigo_qr(codigo_qr, id_funcion):
    return validar_qr(codigo_qr, id_funcion)