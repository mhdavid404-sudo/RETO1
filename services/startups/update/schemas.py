# services/startups/update/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ActualizarStartupRequest(BaseModel):
    """
    Todos los campos son opcionales (actualizacion parcial). Cual de
    ellos se aplica de verdad depende de cuales vino el cliente en el
    body — ver exclude_unset=True en main.py y docs/DECISIONES.md.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    name: Optional[str] = Field(default=None, min_length=1)
    founded_at: Optional[date] = None
    location: Optional[str] = None
    category: Optional[str] = None
    funding_amount: Optional[Decimal] = None


class StartupResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    founded_at: date
    location: Optional[str]
    category: Optional[str]
    funding_amount: Optional[Decimal]
    created_at: datetime
    updated_at: datetime
