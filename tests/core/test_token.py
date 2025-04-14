from pytest import raises
from blog_api.contrib.errors import TokenError
from blog_api.core.token import gen_jwt, verify_jwt


def test_gen_jwt(mock_user_inserted):
    token = gen_jwt(30, mock_user_inserted)

    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_jwt_success(mock_user_inserted):
    mock_user_inserted.role = "user"
    token = gen_jwt(90, mock_user_inserted)

    token_dict = verify_jwt(token)

    assert isinstance(token_dict, dict)
    assert token_dict["sub"] == str(mock_user_inserted.id)
    assert token_dict["role"] == "user"


def test_verify_jwt_raise_expired_signature_error(mock_user_inserted):
    token = gen_jwt(-90, mock_user_inserted)

    with raises(TokenError, match="Token Error: Signature has expired."):
        verify_jwt(token)
