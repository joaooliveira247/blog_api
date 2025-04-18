from unittest.mock import patch
from blog_api.core.security import gen_hash, check_password
from passlib.exc import UnknownHashError
from pytest import raises


def test_gen_hash_success(password: str):
    hash_passwd = gen_hash(password)

    assert len(hash_passwd) == 60
    assert password != hash_passwd


def test_gen_hash_raise_value_error():
    with raises(ValueError) as e:
        gen_hash(None)

    assert str(e.value) == "password must be a string"
    assert isinstance(e.value, ValueError)


def test_check_password_success(password: str):
    hash_passwd = gen_hash(password)

    assert check_password(password, hash_passwd)


def test_check_password_raise_unknow_hash_error(password: str):
    with patch(
        "blog_api.core.security.pwd_context.verify", side_effect=UnknownHashError
    ):
        assert check_password(password, "abcd") is False


def test_check_password_raise_exception(password: str):
    with patch("blog_api.core.security.pwd_context.verify", side_effect=Exception):
        assert check_password(password, "1234") is False
