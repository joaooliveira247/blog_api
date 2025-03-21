from pydantic import BaseModel
from uuid import UUID


class CreatedSchemaMixin(BaseModel):
    id: UUID


class UserCreatedSchema(CreatedSchemaMixin): ...
