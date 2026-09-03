# services/auth/main.py
#
# Microservicio: login (brief seccion 6, "Auth (plus)"). Unico servicio
# con logica de usuarios — valida username/password contra variables de
# entorno (AUTH_USERNAME/AUTH_PASSWORD; sin tabla de usuarios, tal como
# exige el brief) y devuelve un JWT firmado. Los otros 8 servicios
# nunca conocen username/password, solo verifican la firma del token
# (shared/auth.py).
#
# Decisiones que el brief no especifica, confirmadas antes de construir
# (ver docs/DECISIONES.md): nombres de las variables de entorno, claim
# del JWT ({"sub": username}), mensaje generico unico en 401.
#
# El gateway (nginx) mapea POST /v1/api/auth/login directo a la raiz de
# este servicio (mismo patron de strip de prefijo que los otros 8).

import secrets

from fastapi import FastAPI

from shared.auth import crear_token
from shared.config import variable_obligatoria
from shared.cors import configurar_cors
from shared.errors import AuthError, registrar_manejadores_de_errores

from schemas import LoginRequest, LoginResponse

app = FastAPI(title="auth-service")
configurar_cors(app)
registrar_manejadores_de_errores(app)

AUTH_USERNAME = variable_obligatoria("AUTH_USERNAME")
AUTH_PASSWORD = variable_obligatoria("AUTH_PASSWORD")


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.post("/", response_model=LoginResponse)
def login(datos: LoginRequest) -> LoginResponse:
    # secrets.compare_digest en vez de == : comparacion de tiempo
    # constante, evita que la duracion de la respuesta filtre
    # informacion sobre cuantos caracteres coinciden.
    usuario_correcto = secrets.compare_digest(datos.username, AUTH_USERNAME)
    password_correcta = secrets.compare_digest(datos.password, AUTH_PASSWORD)

    if not (usuario_correcto and password_correcta):
        # Mensaje generico unico para ambos casos (usuario inexistente
        # o password incorrecta) — no revela cual de los dos fallo.
        raise AuthError("Credenciales invalidas")

    token = crear_token({"sub": datos.username})
    return LoginResponse(token=token)
