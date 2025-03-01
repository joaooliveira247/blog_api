from pydantic import BaseModel, ConfigDict


class BaseSchemaMixin(BaseModel):
    model = ConfigDict(from_attributes=True)
