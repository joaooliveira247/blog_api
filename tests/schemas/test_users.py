from typing import Any

import pytest
from blog_api.schemas.users import BaseUser
from tests.factories import single_user_data
from pydantic import ValidationError


def test_base_user_schema_success():
    user: dict[str, Any] = single_user_data()
    schema = BaseUser(**user)

    assert schema.model_dump() == user


def test_base_user_schema_username_empty():
    user: dict[str, Any] = single_user_data()
    user.pop("username")

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
    } == {"type": "missing", "loc": ("username",)}


def test_base_user_schema_username_lt_3():
    user: dict[str, Any] = single_user_data()
    user["username"] = "lt"

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
    } == {"type": "string_too_short", "loc": ("username",)}
