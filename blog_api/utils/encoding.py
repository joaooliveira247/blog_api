from datetime import datetime
import json
from typing import Any
from uuid import UUID

from pydantic import BaseModel


def __transform_type_in_str(map: dict[str, Any]) -> dict[str, str]:
    for k, v in map.items():
        match v:
            case UUID():
                map[k] = str(v)
            case datetime():
                map[k] = v.strftime("%d/%m/%Y, %H:%M:%S")

    return map


def encode_pydantic_model(model: BaseModel | list[BaseModel]) -> str | None:
    match model:
        case BaseModel():
            return json.dumps(__transform_type_in_str(model.model_dump()))
        case list():
            models: list[dict[str, Any]] = []

            for m in model:
                models.append(__transform_type_in_str(m.model_dump()))
            return json.dumps(models)
        case _:
            return None
