from blog_api.core.security import gen_hash


def test_gen_hash_success(password: str):
    hash_passwd = gen_hash(password)

    assert len(hash_passwd) == 60
    assert password != hash_passwd
