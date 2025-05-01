from pydantic import BaseModel
from uuid import UUID


class CreatedSchemaMixin(BaseModel):
    id: UUID


class UserCreatedSchema(CreatedSchemaMixin): ...


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UpdateSuccess(BaseModel):
    message: str
