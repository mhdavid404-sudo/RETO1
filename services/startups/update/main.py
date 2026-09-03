# services/startups/update/main.py
#
# Microservicio: actualizar (parcialmente) una startup por id. Protegido
# por JWT (docs/DECISIONES.md). Semantica de actualizacion parcial:
# exclude_unset=True — ver docs/DECISIONES.md para el detalle completo.

from fastapi import Depends, FastAPI

from shared.auth import requerir_autenticacion
from shared.db import obtener_cursor
from shared.errors import NotFoundError, ValidationError, registrar_manejadores_de_errores

from schemas import ActualizarStartupRequest, StartupResponse

app = FastAPI(title="update-startup-service")
registrar_manejadores_de_errores(app)

COLUMNAS = "id, name, founded_at, location, category, funding_amount, created_at, updated_at"
CAMPOS_NO_NULEABLES = {"name", "founded_at"}


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.put("/{startup_id}", response_model=StartupResponse)
def actualizar_startup(
    startup_id: int,
    payload: ActualizarStartupRequest,
    _usuario: dict = Depends(requerir_autenticacion),
) -> StartupResponse:
    campos = payload.model_dump(exclude_unset=True)

    if not campos:
        raise ValidationError(
            "El body no puede estar vacio",
            ["Debe incluir al menos un campo para actualizar"],
        )

    for campo in CAMPOS_NO_NULEABLES:
        if campo in campos and campos[campo] is None:
            raise ValidationError(f"{campo} no puede ser null", [f"{campo} no puede ser null"])

    asignaciones = ", ".join(f"{campo} = %({campo})s" for campo in campos)
    campos["id"] = startup_id

    with obtener_cursor(commit=True) as cursor:
        cursor.execute(
            f"UPDATE startups SET {asignaciones} WHERE id = %(id)s RETURNING {COLUMNAS}",
            campos,
        )
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una startup con id {startup_id}")

    return StartupResponse(**fila)
