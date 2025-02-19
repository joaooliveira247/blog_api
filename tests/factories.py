from faker import Faker

fake: Faker = Faker()


def single_user_data() -> dict:
    return {
        "username": fake.user_name(),
        "email": fake.email(),
    }
