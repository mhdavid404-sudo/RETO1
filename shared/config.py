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

import os


def _variable_obligatoria(nombre: str) -> str:
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
DB_NAME = _variable_obligatoria("DB_NAME")
DB_USER = _variable_obligatoria("DB_USER")
DB_PASSWORD = _variable_obligatoria("DB_PASSWORD")

# --- Autenticación JWT ---
# El secreto de firma es compartido entre auth-service (que firma) y los
# otros 8 servicios (que solo verifican). No puede tener un default: un
# secreto por defecto conocido en el código fuente anularía la seguridad
# del token.
JWT_SECRET = _variable_obligatoria("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60
