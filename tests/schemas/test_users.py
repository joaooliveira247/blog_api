from typing import Any

import pytest
from blog_api.schemas.users import BaseUser, UserIn
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

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("email",),
        "msg": "value is not a valid email address: The part after the @-sign is not valid. It should have a period.",
    }


def test_base_user_schema_email_gt_255():
    user: dict[str, Any] = single_user_data()
    user["email"] = f"{'abcd' * 64}@gmail.com"

    with pytest.raises(ValidationError) as err:
        BaseUser.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("email",),
        "msg": "value is not a valid email address: The email address is too long before the @-sign (192 characters too many).",
    }


def test_user_in_return_success():
    user: dict[str, Any] = single_user_data()
    user["password"] = "Abc@1234"
    schema = UserIn(**user)
    user.pop("password")

    assert schema.model_dump(exclude={"password"}) == user


def test_user_in_password_lt_8_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "Abc@123"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "string_too_short",
        "loc": ("password",),
        "msg": "String should have at least 8 characters",
    }


def test_user_in_password_gt_128_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = f"Abc@123{'1234' * 64}"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "string_too_long",
        "loc": ("password",),
        "msg": "String should have at most 128 characters",
    }


def test_user_in_password_without_upper_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "abc@1234"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: upper",
    }


def test_user_in_password_without_digit_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "Abc@abcd"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: digit",
    }


def test_user_in_password_without_special_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "Abc1abcd"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: special",
    }


def test_user_in_password_without_lower_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "ABC@1234"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: lower",
    }


def test_user_in_password_without_lower_and_upper_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "4002@8922"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: lower, upper",
    }


def test_user_in_password_without_lower_upper_special_raise_validation_error():
    user: dict[str, Any] = single_user_data()
    user["password"] = "40028922"

    with pytest.raises(ValidationError) as err:
        UserIn.model_validate(user)

    assert {
        "type": err.value.errors()[0]["type"],
        "loc": err.value.errors()[0]["loc"],
        "msg": err.value.errors()[0]["msg"],
    } == {
        "type": "value_error",
        "loc": ("password",),
        "msg": "Value error, Wrong password format! characters missing: lower, upper, special",
    }
