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


def test_base_user_schema_username_gt_255():
    user: dict[str, Any] = single_user_data()
    user["username"] = "abcd" * 64

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
    } == {"type": "string_too_long", "loc": ("username",)}


def test_base_user_schema_username_invalid_type():
    user: dict[str, Any] = single_user_data()
    user["username"] = 123456

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
    } == {"type": "string_type", "loc": ("username",)}


def test_base_user_schema_email_value_error():
    user: dict[str, Any] = single_user_data()
    user["email"] = "a@a"

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    print(err.value.errors()[0])

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("email",),
        "msg": "value is not a valid email address: The part after the @-sign is not valid. It should have a period.",
    }
