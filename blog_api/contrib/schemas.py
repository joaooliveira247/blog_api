from pydantic import BaseModel, ConfigDict, UUID4, Field
from datetime import datetime


class BaseSchemaMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OutMixin(BaseSchemaMixin):
    id: UUID4 = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
