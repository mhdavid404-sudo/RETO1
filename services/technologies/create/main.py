# services/technologies/create/main.py
#
# Microservicio: crear una tecnologia. Mismo esqueleto que
# create-startup-service (ver ese servicio para el detalle explicado).
# Protegido por JWT.

from fastapi import Depends, FastAPI, status

from shared.auth import requerir_autenticacion
from shared.db import obtener_cursor
from shared.errors import registrar_manejadores_de_errores

from schemas import CrearTechnologyRequest, TechnologyResponse

app = FastAPI(title="create-technology-service")
registrar_manejadores_de_errores(app)


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.post("/", status_code=status.HTTP_201_CREATED, response_model=TechnologyResponse)
def crear_technology(
    datos: CrearTechnologyRequest,
    _usuario: dict = Depends(requerir_autenticacion),
) -> TechnologyResponse:
    with obtener_cursor(commit=True) as cursor:
        cursor.execute(
            """
            INSERT INTO technologies (name, sector, description, adoption_level)
            VALUES (%(name)s, %(sector)s, %(description)s, %(adoption_level)s)
            RETURNING id, name, sector, description, adoption_level,
                      created_at, updated_at
            """,
            datos.model_dump(),
        )
        fila_creada = cursor.fetchone()

    return TechnologyResponse(**fila_creada)
