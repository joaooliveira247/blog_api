from typing import Any
from blog_api.schemas.users import BaseUser
from tests.factories import single_user_data


def test_base_user_schema_success():
    user: dict[str, Any] = single_user_data()
    schema = BaseUser(**user)

    assert schema.model_dump() == user
