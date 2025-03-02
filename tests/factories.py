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


def single_post_data() -> dict:
    return {
        "title": "fake blog post",
        "categories": ["fake", "mock", "factory"],
        "content": fake.text(),
    }


def many_posts_data() -> list[dict]:
    return [
        {
            "id": fake.uuid4(),
            "title": "Post 1: Introdução ao Python",
            "categories": ["Python", "Introdução"],
            "content": "Este post fala sobre o básico do Python.",
            "author": fake.user_name(),
        },
        {
            "id": fake.uuid4(),
            "title": "Post 2: Avançando em Python",
            "categories": ["Python", "Avançado"],
            "content": "Este post aborda tópicos mais avançados em Python.",
            "author": fake.user_name(),
        },
        {
            "id": fake.uuid4(),
            "title": "Post 3: Dicas de Carreira em Tecnologia",
            "categories": ["Carreira", "Tecnologia"],
            "content": "Neste post, damos dicas sobre como crescer na carreira de tecnologia.",
            "author": fake.user_name(),
        },
        {
            "id": fake.uuid4(),
            "title": "Post 4: Introdução ao Machine Learning",
            "categories": ["Machine Learning", "Inteligência Artificial"],
            "content": "Aqui discutimos o início no mundo do Machine Learning.",
            "author": fake.user_name(),
        },
        {
            "id": fake.uuid4(),
            "title": "Post 5: Como Aprender a Programar",
            "categories": ["Carreira", "Desenvolvimento Pessoal"],
            "content": "Este post oferece dicas para quem quer começar a programar.",
            "author": fake.user_name(),
        },
    ]
