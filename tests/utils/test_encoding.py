import json

from blog_api.utils.encoding import encode_pydantic_model
from blog_api.models.users import UserModel


def test_encode_pydantic_model_success(mock_user_out_inserted):
    encoded = encode_pydantic_model(mock_user_out_inserted)
    assert_item: dict[str, str] = {
        "id": str(mock_user_out_inserted.id),
        "created_at": mock_user_out_inserted.created_at.isoformat(),
        "updated_at": mock_user_out_inserted.updated_at.isoformat(),
        "username": mock_user_out_inserted.username,
        "email": mock_user_out_inserted.email,
        "role": mock_user_out_inserted.role,
    }

    assert encoded == json.dumps(assert_item)


def test_encode_pydandtic_model_return_empty_list():
    encoded = encode_pydantic_model(list())
    assert encoded == "[]"


def test_encode_pydantic_model_return_none():
    encoded = encode_pydantic_model(UserModel())
    assert encoded is None
