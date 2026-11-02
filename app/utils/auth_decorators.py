from flask import session, jsonify

def admin_required(fn):
    def wrapper(*args, **kwargs):
        if not session.get("id_usuario"):
            return (
                jsonify({"status":"error",
                         "code":"NO_AUTENTICADO",
                         "message":"Sesion requerida"
                         }),
                         401,
            )
        if session.get("rol") != "ADMIN":
            return (
                jsonify({"status":"error",
                         "code":"PERMISO_DENEGADO",
                         "message":"Solo ADMIN puede usar este recurso"}),
                         403,
            )
        return fn(*args, **kwargs)
    return wrapper