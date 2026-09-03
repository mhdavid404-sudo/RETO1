# services/startups/read/main.py
#
# Microservicio: leer startups (listar con filtros opcionales, o detalle
# por id). Sin autenticacion (docs/DECISIONES.md: read queda publico).
#
# Filtro `name`: coincidencia parcial insensible a mayusculas (ILIKE),
# pensado como busqueda. Filtro `category`: coincidencia exacta, por ser
# un valor categorico. Decision menor de comportamiento, no de negocio.

from typing import Optional

from fastapi import FastAPI, Query

from shared.db import obtener_cursor
from shared.errors import NotFoundError, registrar_manejadores_de_errores

from schemas import StartupResponse

app = FastAPI(title="read-startup-service")
registrar_manejadores_de_errores(app)

COLUMNAS = "id, name, founded_at, location, category, funding_amount, created_at, updated_at"


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.get("/", response_model=list[StartupResponse])
def listar_startups(
    name: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
) -> list[StartupResponse]:
    condiciones = []
    parametros: dict = {}
    if name is not None:
        condiciones.append("name ILIKE %(name)s")
        parametros["name"] = f"%{name}%"
    if category is not None:
        condiciones.append("category = %(category)s")
        parametros["category"] = category

    consulta = f"SELECT {COLUMNAS} FROM startups"
    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)
    consulta += " ORDER BY id"

    with obtener_cursor() as cursor:
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

    return [StartupResponse(**fila) for fila in filas]


@app.get("/{startup_id}", response_model=StartupResponse)
def obtener_startup(startup_id: int) -> StartupResponse:
    with obtener_cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS} FROM startups WHERE id = %(id)s", {"id": startup_id})
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una startup con id {startup_id}")

    return StartupResponse(**fila)
