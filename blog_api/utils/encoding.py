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
                map[k] = v.isoformat()

    return map


def __transform_str_in_type(
    map: dict[str, Any],
) -> dict[str, str]:
    for k, v in map.items():
        if k == "created_at" or k == "updated_at":
            map[k] = datetime.fromisoformat(v)

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
