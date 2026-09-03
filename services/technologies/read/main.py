# services/technologies/read/main.py
#
# Microservicio: leer tecnologias (listar con filtros opcionales, o
# detalle por id). Sin autenticacion. Filtros sector/adoptionLevel:
# coincidencia exacta (brief seccion 6 no menciona filtro por name aqui,
# a diferencia de startups).

from typing import Optional

from fastapi import FastAPI, Query

from shared.cors import configurar_cors
from shared.db import obtener_cursor
from shared.errors import NotFoundError, registrar_manejadores_de_errores

from schemas import TechnologyResponse

app = FastAPI(title="read-technology-service")
configurar_cors(app)
registrar_manejadores_de_errores(app)

COLUMNAS = "id, name, sector, description, adoption_level, created_at, updated_at"


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.get("/", response_model=list[TechnologyResponse])
def listar_technologies(
    sector: Optional[str] = Query(default=None),
    adoption_level: Optional[str] = Query(default=None, alias="adoptionLevel"),
) -> list[TechnologyResponse]:
    condiciones = []
    parametros: dict = {}
    if sector is not None:
        condiciones.append("sector = %(sector)s")
        parametros["sector"] = sector
    if adoption_level is not None:
        condiciones.append("adoption_level = %(adoption_level)s")
        parametros["adoption_level"] = adoption_level

    consulta = f"SELECT {COLUMNAS} FROM technologies"
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY id"

    with obtener_cursor() as cursor:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

    return [TechnologyResponse(**fila) for fila in filas]


@app.get("/{technology_id}", response_model=TechnologyResponse)
def obtener_technology(technology_id: int) -> TechnologyResponse:
    with obtener_cursor() as cursor:
        cursor.execute(
            f"SELECT {COLUMNAS} FROM technologies WHERE id = %(id)s", {"id": technology_id}
        )
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una tecnologia con id {technology_id}")

    return TechnologyResponse(**fila)
