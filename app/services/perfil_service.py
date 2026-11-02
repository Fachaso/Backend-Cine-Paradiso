from app.repositories.perfil_repository import obtener_usuario_por_id, listar_compras_por_usuario

def _formatear_compra(compra):
    compra = dict(compra)
    compra["monto_total"] = float(compra["monto_total"])
    compra["fecha_compra"] = compra["fecha_compra"].isoformat()
    return compra


def obtener_perfil(id_usuario):
    usuario = obtener_usuario_por_id(id_usuario)
    if usuario is None:
        return None, "USUARIO_NO_ENCONTRADO"
    compras = listar_compras_por_usuario(id_usuario)
    compras = [_formatear_compra(compra) for compra in compras]
    return {"usuario": usuario, "compras": compras}, None
