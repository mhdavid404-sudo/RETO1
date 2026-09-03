# shared/config.py
#
# Punto único de lectura de variables de entorno. Ningún microservicio debe
# leer os.environ directamente: todos importan este módulo. Así, si cambia
# el nombre de una variable o su valor por defecto, se cambia en un solo
# lugar y no en 9 servicios distintos.
#
# Decisión de diseño: las variables sin valor por defecto razonable
# (credenciales, secretos) son obligatorias y se valida su presencia al
# importar el módulo, no al usarlas. Si falta una, el servicio no debe
# arrancar "a medias" — mejor un fallo inmediato y explícito al iniciar
# el contenedor que un error confuso más tarde en medio de una petición.
#
# Importante: solo las variables que TODOS los servicios necesitan (la
# conexión a la DB) viven aquí. JWT_SECRET vive en shared/auth.py, no
# aquí — si estuviera en este módulo, importar shared.config (algo que
# hace shared/db.py, y por lo tanto todo servicio) obligaria incluso a
# los servicios de solo lectura a tener JWT_SECRET configurado, aunque
# nunca lo usen. variable_obligatoria() queda publica para que
# shared/auth.py la reutilice con el mismo criterio de fallo rapido.

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


# --- Base de datos PostgreSQL ---
# Host y puerto sí tienen un valor por defecto razonable para desarrollo
# local con docker-compose (el servicio de la DB se llama "db" en la red
# interna de Docker). Nombre, usuario y contraseña no tienen default:
# son específicos de cada entorno y deben venir del .env.
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = variable_obligatoria("DB_NAME")
DB_USER = variable_obligatoria("DB_USER")
DB_PASSWORD = variable_obligatoria("DB_PASSWORD")
