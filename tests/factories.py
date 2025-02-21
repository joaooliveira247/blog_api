from faker import Faker
from blog_api.core.security import gen_hash

fake: Faker = Faker()


def single_user_data() -> dict:
    return {
        "username": fake.user_name(),
        "email": fake.email(),
    }


def many_users_data() -> list[dict]:
    hash_pass: list[str] = []

    for _ in range(4):
        hash_pass.append(gen_hash(fake.password()))

    return [
        {
            "id": fake.uuid4(),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": passwd,
            "role": "user",
        }
        for passwd in hash_pass
    ]
