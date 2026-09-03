# services/technologies/update/main.py
#
# Microservicio: actualizar (parcialmente) una tecnologia por id. Mismo
# patron que update-startup-service (exclude_unset=True — ver
# docs/DECISIONES.md).

from fastapi import Depends, FastAPI

from shared.auth import requerir_autenticacion
from shared.db import obtener_cursor
from shared.errors import NotFoundError, ValidationError, registrar_manejadores_de_errores

from schemas import ActualizarTechnologyRequest, TechnologyResponse

app = FastAPI(title="update-technology-service")
registrar_manejadores_de_errores(app)

COLUMNAS = "id, name, sector, description, adoption_level, created_at, updated_at"
CAMPOS_NO_NULEABLES = {"name", "sector"}


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.put("/{technology_id}", response_model=TechnologyResponse)
def actualizar_technology(
    technology_id: int,
    payload: ActualizarTechnologyRequest,
    _usuario: dict = Depends(requerir_autenticacion),
) -> TechnologyResponse:
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
    campos["id"] = technology_id

    with obtener_cursor(commit=True) as cursor:
        cursor.execute(
            f"UPDATE technologies SET {asignaciones} WHERE id = %(id)s RETURNING {COLUMNAS}",
            campos,
        )
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una tecnologia con id {technology_id}")

    return TechnologyResponse(**fila)
