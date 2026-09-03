# services/auth/schemas.py
#
# El brief (seccion 4) no lista schemas.py para auth/, solo main.py,
# Dockerfile, requirements.txt y .env.example. Se agrega igual, por
# consistencia con el patron de validacion ya usado en los otros 8
# servicios — no cambia el contrato de la API (body/response siguen
# siendo exactamente {username, password} / {token} segun brief
# seccion 6).

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
