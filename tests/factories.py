from faker import Faker
from blog_api.core.security import gen_hash

fake: Faker = Faker()


def single_user_data() -> dict:
    hash_password = gen_hash(fake.password)

    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": hash_password,
    }
