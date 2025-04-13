from blog_api.core.token import gen_jwt


def test_gen_jwt(mock_user_inserted):
    token = gen_jwt(30, mock_user_inserted)

    assert isinstance(token, str)
    assert len(token) > 0
