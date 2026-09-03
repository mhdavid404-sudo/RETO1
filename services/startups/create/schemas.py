# services/startups/create/schemas.py
#
# Contrato de datos de este servicio, validado por Pydantic.
#
# El payload que llega por HTTP usa camelCase (foundedAt, fundingAmount)
# porque asi lo fija el contrato de API del brief (seccion 6). Puertas
# adentro (Python, base de datos) se usa snake_case, que es la convencion
# natural de ambos. alias_generator=to_camel resuelve esa traduccion sin
# tener que escribir dos nombres por campo a mano.

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CrearStartupRequest(BaseModel):
    """
    Cuerpo esperado por POST /. Campo `name` y `founded_at` son
    obligatorios (regla del modelo de datos, brief seccion 5); el resto
    es opcional. extra="forbid": cualquier campo fuera de esta lista se
    rechaza con 400, en vez de ignorarse en silencio.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    name: str = Field(min_length=1)
    founded_at: date
    location: Optional[str] = None
    category: Optional[str] = None
    funding_amount: Optional[Decimal] = None


class StartupResponse(BaseModel):
    """Representa la fila creada, tal como se devuelve al cliente."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    founded_at: date
    location: Optional[str]
    category: Optional[str]
    funding_amount: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
