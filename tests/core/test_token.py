from unittest.mock import patch
from pytest import raises
from blog_api.contrib.errors import GenericError, TokenError
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


def test_verify_jwt_raise_token_error():
    with raises(TokenError, match="Token Error: Not enough segments"):
        verify_jwt("12345")


def test_verify_jwt_raise_generic_erorr():
    with patch(
        "blog_api.core.token.jwt.decode", side_effect=Exception("unmapped error")
    ):
        with raises(GenericError, match="unmapped error"):
            verify_jwt("12345")
