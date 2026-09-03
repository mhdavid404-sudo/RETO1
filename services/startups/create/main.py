# services/startups/create/main.py
#
# Microservicio: crear una startup. Responsabilidad unica: recibir el
# POST, validar el body (schemas.CrearStartupRequest), insertar la fila
# en la tabla `startups` y devolver el recurso creado con 201.
#
# El gateway (nginx) hace strip del prefijo /v1/api/startups/create y
# reenvia aqui como POST / — por eso el endpoint esta en la raiz y no en
# "/create". Protegido por JWT (ver docs/DECISIONES.md): solo se puede
# crear con un token valido.

from fastapi import Depends, FastAPI, status

from shared.auth import requerir_autenticacion
from shared.cors import configurar_cors
from shared.db import obtener_cursor
from shared.errors import registrar_manejadores_de_errores

from schemas import CrearStartupRequest, StartupResponse

app = FastAPI(title="create-startup-service")
configurar_cors(app)
registrar_manejadores_de_errores(app)


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.post("/", status_code=status.HTTP_201_CREATED, response_model=StartupResponse)
def crear_startup(
    datos: CrearStartupRequest,
    _usuario: dict = Depends(requerir_autenticacion),
) -> StartupResponse:
    with obtener_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO startups (name, founded_at, location, category, funding_amount)
            VALUES (%(name)s, %(founded_at)s, %(location)s, %(category)s, %(funding_amount)s)
            RETURNING id, name, founded_at, location, category, funding_amount,
                      created_at, updated_at
            """,
            datos.model_dump(),
        )
        fila_creada = cursor.fetchone()

    return StartupResponse(**fila_creada)
