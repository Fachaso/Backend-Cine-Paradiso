
from app.repositories.compra_repository import (
    crear_compra_pendiente as crear_compra_pendiente_repositorio,
    confirmar_compra as confirmar_compra_repositorio,
    cancelar_compra as cancelar_compra_repositorio,
    obtener_compra as obtener_compra_repositorio,
)


def crear_compra_pendiente(id_usuario, datos):
    return crear_compra_pendiente_repositorio(id_usuario, datos)


def confirmar_compra(id_compra, id_usuario, datos):
    return confirmar_compra_repositorio(id_compra, id_usuario, datos)


def obtener_compra(id_compra, id_usuario):
    return obtener_compra_repositorio(id_compra, id_usuario)


def cancelar_compra(id_compra, id_usuario):
    return cancelar_compra_repositorio(id_compra, id_usuario)
