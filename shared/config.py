# shared/config.py
#
# Unico contenido: variable_obligatoria(), el helper para leer una
# variable de entorno obligatoria y fallar rapido (al importar el
# modulo que la usa, no a mitad de un request) si falta.
#
# Deliberadamente NO define aqui ninguna variable concreta (ni de DB ni
# de JWT). Motivo (lección de un bug real, ver docs/DECISIONES.md):
# Python ejecuta el modulo COMPLETO al importarlo, sin importar que
# nombre se use de el. Si este archivo definiera, por ejemplo, las
# variables de DB, cualquier modulo que solo necesite el helper (como
# shared/auth.py) arrastraria consigo la obligacion de tener la DB
# configurada, aunque nunca la use. Por eso cada modulo de shared/
# (db.py, auth.py) declara sus propias variables, usando este helper,
# y solo los servicios que importan ESE modulo especifico heredan esa
# obligacion.

import os


def variable_obligatoria(nombre: str) -> str:
    """Lee una variable de entorno obligatoria; falla rápido si no existe."""
    valor = os.getenv(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria: {nombre}. "
            f"Revisa el archivo .env del servicio (ver .env.example)."
        )
    return valor
