# services/startups/read/schemas.py
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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
