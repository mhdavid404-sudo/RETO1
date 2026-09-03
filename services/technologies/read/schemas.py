# services/technologies/read/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    sector: str
    description: Optional[str]
    adoption_level: Optional[str]
    created_at: datetime
    updated_at: datetime
