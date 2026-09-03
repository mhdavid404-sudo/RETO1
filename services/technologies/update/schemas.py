# services/technologies/update/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ActualizarTechnologyRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    name: Optional[str] = Field(default=None, min_length=1)
    sector: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    adoption_level: Optional[str] = None


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    sector: str
    description: Optional[str]
    adoption_level: Optional[str]
    created_at: datetime
    updated_at: datetime
