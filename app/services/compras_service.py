from app.repositories.compra_repository import (
    crear_compra_pendiente as crear_compra_pendiente_repositorio,
    confirmar_compra as confirmar_compra_repositorio,
    cancelar_compra as cancelar_compra_repositorio,
    obtener_compra as obtener_compra_repositorio,
    eliminar_compra_pendiente as eliminar_compra_pendiente_repositorio,
)


def crear_compra(id_usuario, datos):
    pendiente, error, status = crear_compra_pendiente_repositorio(id_usuario, datos)
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

    compra, error, status = obtener_compra_repositorio(id_compra, id_usuario)
    if error is not None:
        return None, error, status

    cabecera = {
        clave: valor for clave, valor in compra.items()
        if clave not in ("entradas", "servicios")
    }
    return {
        "compra": cabecera,
        "entradas": compra.get("entradas", []),
        "servicios": compra.get("servicios", []),
    }, None, 201


def confirmar_compra(id_compra, id_usuario, datos):
    return confirmar_compra_repositorio(id_compra, id_usuario, datos)


def obtener_compra(id_compra, id_usuario):
    return obtener_compra_repositorio(id_compra, id_usuario)


def cancelar_compra(id_compra, id_usuario):
    return cancelar_compra_repositorio(id_compra, id_usuario)
