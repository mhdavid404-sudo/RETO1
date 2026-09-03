# shared/db.py
#
# Manejo de la conexión a PostgreSQL. Cada microservicio abre una conexion
# nueva por cada request y la cierra al terminar — no se usa un pool de
# conexiones. Es una decision deliberada: con 9 servicios livianos y el
# volumen esperado de este reto, un pool agrega complejidad de
# configuracion y ciclo de vida (cuando inicializarlo, cuando cerrarlo,
# tamaño) que no se justifica aqui. Si el trafico real lo exigiera, seria
# el primer cambio a evaluar, pero no forma parte del alcance del reto.
#
# Las variables DB_* se definen aqui (no en shared/config.py): solo los
# servicios que importan shared.db necesitan la DB configurada.
# auth-service, por ejemplo, no toca la base de datos en absoluto y por
# lo tanto no importa este modulo (ver docs/DECISIONES.md).

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
import psycopg2.extras

from shared.config import variable_obligatoria

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = variable_obligatoria("DB_NAME")
DB_USER = variable_obligatoria("DB_USER")
DB_PASSWORD = variable_obligatoria("DB_PASSWORD")


@contextmanager
def obtener_cursor(commit: bool = False) -> Iterator["psycopg2.extras.RealDictCursor"]:
    """
    Abre una conexion, entrega un cursor que devuelve cada fila como dict
    (RealDictCursor), y garantiza que la conexion se cierre siempre al
    salir del bloque `with`, haya o no error.

    commit=True: confirma la transaccion al salir sin errores (usar en
    create/update/delete). commit=False (default): solo lectura, no hace
    falta confirmar nada (usar en read).

    Si ocurre una excepcion dentro del bloque, se hace rollback antes de
    relanzarla — nunca se deja una transaccion a medias.
    """
    conexion = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    try:
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        yield cursor
        if commit:
            conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
