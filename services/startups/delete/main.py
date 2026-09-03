# services/startups/delete/main.py
#
# Microservicio: eliminar una startup por id. Protegido por JWT. Sin
# schemas.py: no hay body que validar, solo el id de la ruta (FastAPI ya
# valida que sea int).

from fastapi import Depends, FastAPI, status

from shared.auth import requerir_autenticacion
from shared.cors import configurar_cors
from shared.db import obtener_cursor
from shared.errors import NotFoundError, registrar_manejadores_de_errores

app = FastAPI(title="delete-startup-service")
configurar_cors(app)
registrar_manejadores_de_errores(app)


@app.get("/health")
def salud() -> dict:
    return {"status": "ok"}


@app.delete("/{startup_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_startup(
    startup_id: int,
    _usuario: dict = Depends(requerir_autenticacion),
) -> None:
    with obtener_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM startups WHERE id = %(id)s RETURNING id", {"id": startup_id})
        fila = cursor.fetchone()

    if fila is None:
        raise NotFoundError(f"No existe una startup con id {startup_id}")
