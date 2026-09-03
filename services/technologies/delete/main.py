# services/technologies/delete/main.py
#
# Microservicio: eliminar una tecnologia por id. Mismo patron que
# delete-startup-service. Protegido por JWT.

from fastapi import Depends, FastAPI, status

from shared.auth import requerir_autenticacion
from shared.db import obtener_cursor
from shared.errors import NotFoundError, registrar_manejadores_de_errores

app = FastAPI(title="delete-technology-service")
registrar_manejadores_de_errores(app)


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.delete("/{technology_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_technology(
    technology_id: int,
    _usuario: dict = Depends(requerir_autenticacion),
) -> None:
    with obtener_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM technologies WHERE id = %(id)s RETURNING id", {"id": technology_id}
        )
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una tecnologia con id {technology_id}")
