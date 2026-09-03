# shared/auth.py
#
# Creacion y verificacion de JWT. Solo auth-service llama a crear_token();
# los otros 8 servicios solo llaman a verificar_token() para proteger sus
# endpoints. Ninguno de los 9 servicios tiene logica propia de usuarios:
# eso vive unicamente en auth-service (ver shared/config.py sobre el
# secreto compartido).

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header

from shared.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES
from shared.errors import AuthError


def crear_token(datos: dict) -> str:
    """Firma un JWT con los datos dados mas una expiracion de 1 hora."""
    ahora = datetime.now(timezone.utc)
    payload = {
        **datos,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=JWT_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verificar_token(token: str) -> dict:
    """
    Verifica firma y expiracion del token. Devuelve el payload si es
    valido. Si es invalido o expiro, lanza AuthError — nunca se deja
    pasar un token roto en silencio.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthError("El token expiro")
    except jwt.InvalidTokenError:
        raise AuthError("Token invalido")


def requerir_autenticacion(authorization: str | None = Header(default=None)) -> dict:
    """
    Dependencia de FastAPI para proteger endpoints de escritura
    (create/update/delete — ver docs/DECISIONES.md sobre el alcance).
    Uso: `def crear_x(..., usuario: dict = Depends(requerir_autenticacion))`.

    Lee el header "Authorization: Bearer <token>", verifica el token y
    devuelve su payload. Si el header falta o el token es invalido,
    lanza AuthError (401) — manejado de forma uniforme por
    shared/errors.py, igual que cualquier otro error de la aplicacion.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError("Falta el header Authorization: Bearer <token>")
    token = authorization.removeprefix("Bearer ").strip()
    return verificar_token(token)
