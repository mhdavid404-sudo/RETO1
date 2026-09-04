# shared/errors.py
#
# Formato de error uniforme para los 9 servicios:
#   { "message": "...", "details": [...] }
# Cada servicio llama a registrar_manejadores_de_errores(app) una sola vez,
# justo después de crear su instancia de FastAPI. Así ningún servicio
# construye su propio JSON de error a mano: se lanzan estas excepciones
# desde cualquier parte del código y el formato de respuesta queda
# garantizado igual en los 9 servicios.

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shared.cors import FRONTEND_ORIGIN


class ErrorAplicacion(Exception):
    """Base de todos los errores de negocio manejados por estos servicios."""

    codigo_http = 500

    def __init__(self, mensaje: str, detalles: list[str] | None = None):
        self.mensaje = mensaje
        self.detalles = detalles or [mensaje]
        super().__init__(mensaje)


class ValidationError(ErrorAplicacion):
    """Datos de entrada inválidos o campos no permitidos. -> 400"""

    codigo_http = 400


class NotFoundError(ErrorAplicacion):
    """El recurso solicitado no existe. -> 404"""

    codigo_http = 404


class AuthError(ErrorAplicacion):
    """Token ausente, inválido o expirado. -> 401"""

    codigo_http = 401


def _respuesta_error(codigo_http: int, mensaje: str, detalles: list[str]) -> JSONResponse:
    return JSONResponse(
        status_code=codigo_http,
        content={"message": mensaje, "details": detalles},
    )


def registrar_manejadores_de_errores(app: FastAPI) -> None:
    """Registra los exception handlers en la app de FastAPI del servicio."""

    @app.exception_handler(ErrorAplicacion)
    async def _manejar_error_aplicacion(request: Request, exc: ErrorAplicacion):
        return _respuesta_error(exc.codigo_http, exc.mensaje, exc.detalles)

    @app.exception_handler(RequestValidationError)
    async def _manejar_error_validacion_fastapi(request: Request, exc: RequestValidationError):
        # Errores de validación automáticos de Pydantic (tipo incorrecto,
        # campo obligatorio faltante, extra="forbid" violado, etc.) se
        # traducen al mismo formato uniforme en vez de dejar pasar el
        # formato por defecto de FastAPI.
        detalles = [
            f"{'.'.join(str(p) for p in error['loc'] if p != 'body')}: {error['msg']}"
            for error in exc.errors()
        ]
        return _respuesta_error(400, "Validation error", detalles)

    @app.exception_handler(Exception)
    async def _manejar_error_no_controlado(request: Request, exc: Exception):
        # Ultima red de seguridad: cualquier excepcion no anticipada se
        # responde con el mismo formato en vez de filtrar un traceback
        # o el error generico por defecto de FastAPI/Starlette.
        #
        # CORS manual aqui (bug real encontrado probando el front en
        # navegador, ver docs/DECISIONES.md): Starlette enruta los
        # handlers registrados para la clase base `Exception` a
        # ServerErrorMiddleware, que queda POR FUERA de CORSMiddleware
        # en el stack — CORSMiddleware nunca ve esta respuesta, asi que
        # nunca le agrega el header Access-Control-Allow-Origin. Los
        # otros handlers (ErrorAplicacion, RequestValidationError) no
        # tienen este problema porque Starlette los enruta por
        # ExceptionMiddleware, que si esta dentro de CORSMiddleware.
        respuesta = _respuesta_error(500, "Internal server error", [str(exc)])
        origen = request.headers.get("origin")
        if origen == FRONTEND_ORIGIN:
            respuesta.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
            respuesta.headers["Access-Control-Allow-Credentials"] = "true"
        return respuesta
