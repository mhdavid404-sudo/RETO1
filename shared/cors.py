# shared/cors.py
#
# CORS restringido al dominio del front (requisito del documento
# oficial del reto — no aparece textualmente en RETO1-BRIEF.md, que es
# un resumen, pero es una regla vigente confirmada por el Product
# Owner). Se implementa aqui, en cada servicio FastAPI, y no en Nginx:
# el gateway solo enruta (brief seccion 3, "no valida, no transforma,
# no decide"), y decidir que origenes se aceptan es una decision de
# politica, no ruteo puro. Ver docs/DECISIONES.md.
#
# Cada uno de los 9 servicios llama a configurar_cors(app) justo
# despues de crear su instancia de FastAPI.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import variable_obligatoria

FRONTEND_ORIGIN = variable_obligatoria("FRONTEND_ORIGIN")


def configurar_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
