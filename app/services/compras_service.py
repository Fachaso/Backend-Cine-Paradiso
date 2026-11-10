from flask import current_app

from app.repositories.compra_repository import (
    crear_compra_pendiente as crear_compra_pendiente_repositorio,
    confirmar_compra as confirmar_compra_repositorio,
    cancelar_compra as cancelar_compra_repositorio,
    obtener_compra as obtener_compra_repositorio,
    eliminar_compra_pendiente as eliminar_compra_pendiente_repositorio,
    obtener_datos_pelicula_compra as obtener_datos_pelicula_compra_repositorio,
)
from app.repositories.usuario_email_repository import obtener_email_usuario
from app.services.email_service import enviar_comprobante_compra


def _enviar_comprobante(id_usuario, datos_compra):
    id_compra = datos_compra.get("compra", {}).get("id_compra")

    current_app.logger.info(
        "Iniciando envío del comprobante para la compra %s",
        id_compra,
    )

    try:
        email = obtener_email_usuario(id_usuario)
        if not email:
            current_app.logger.warning(
                "No se encontró email para el usuario %s",
                id_usuario,
            )
            return

        try:
            pelicula = (
                obtener_datos_pelicula_compra_repositorio(id_compra) or {}
            )
        except Exception:
            # Un problema al obtener el póster no impide enviar el comprobante.
            current_app.logger.exception(
                "No se pudieron obtener los datos de película"
            )
            pelicula = {}

        datos_email = dict(datos_compra)
        datos_email["pelicula"] = pelicula

        respuesta_resend = enviar_comprobante_compra(email, datos_email)

        current_app.logger.info(
            "US18: Resend aceptó la compra %s; email_id=%s",
            id_compra,
            respuesta_resend.get("id"),
        )
    except Exception:
        current_app.logger.exception(
            "Falló el envío del comprobante de la compra %s",
            id_compra,
        )

def crear_compra(id_usuario, datos):
    pendiente, error, status = crear_compra_pendiente_repositorio(
        id_usuario, datos
    )
    if error is not None:
        return None, error, status

    id_compra = pendiente["id_compra"]
    datos_confirmacion = {"servicios": datos.get("servicios", [])}

    try:
        _, error, status = confirmar_compra_repositorio(
            id_compra, id_usuario, datos_confirmacion
        )
    except Exception:
        eliminar_compra_pendiente_repositorio(id_compra)
        raise

    if error is not None:
        eliminar_compra_pendiente_repositorio(id_compra)
        return None, error, status

    compra, error, status = obtener_compra_repositorio(
        id_compra, id_usuario
    )
    if error is not None:
        return None, error, status

    cabecera = {
        clave: valor
        for clave, valor in compra.items()
        if clave not in ("entradas", "servicios")
    }
    resultado = {
        "compra": cabecera,
        "entradas": compra.get("entradas", []),
        "servicios": compra.get("servicios", []),
    }

    # Se ejecuta después de confirmar y leer la compra.
    _enviar_comprobante(id_usuario, resultado)

    return resultado, None, 201


def confirmar_compra(id_compra, id_usuario, datos):
    return confirmar_compra_repositorio(id_compra, id_usuario, datos)


def obtener_compra(id_compra, id_usuario):
    return obtener_compra_repositorio(id_compra, id_usuario)


def cancelar_compra(id_compra, id_usuario):
    return cancelar_compra_repositorio(id_compra, id_usuario)
