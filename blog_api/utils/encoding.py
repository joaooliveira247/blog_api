from datetime import datetime
from typing import Any
from uuid import UUID


def __transform_type_in_str(map: dict[str, Any]) -> dict[str, str]:
    for k, v in map.items():
        match v:
            case UUID():
                map[k] = str(v)
            case datetime():
                map[k] = v.strftime("%d/%m/%Y, %H:%M:%S")

    return map
