from datetime import datetime

from faker import Faker
from faker.providers import date_time

from blog_api.core.security import gen_hash

fake: Faker = Faker()
fake.add_provider(date_time)


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
    created_at_posts = [
        datetime.combine(
            fake.date_between(start_date="-1y", end_date="+1w"),
            datetime.min.time(),
        ).timestamp()
        for _ in range(5)
    ]

    posts: list[dict] = [
        {
            "id": fake.uuid4(),
            "title": "Post 1: Introdução ao Python",
            "categories": ["Python", "Introdução"],
            "content": "Este post fala sobre o básico do Python.",
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
            "created_at": created_at_posts[0],
            "updated_at": created_at_posts[0],
        },
        {
            "id": fake.uuid4(),
            "title": "Post 2: Avançando em Python",
            "categories": ["Python", "Avançado"],
            "content": "Este post aborda tópicos mais avançados em Python.",
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
            "created_at": created_at_posts[1],
            "updated_at": created_at_posts[1],
        },
        {
            "id": fake.uuid4(),
            "title": "Post 3: Dicas de Carreira em Tecnologia",
            "categories": ["Carreira", "Tecnologia"],
            "content": "Neste post, damos dicas sobre como crescer na carreira de tecnologia.",
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
            "created_at": created_at_posts[2],
            "updated_at": created_at_posts[2],
        },
        {
            "id": fake.uuid4(),
            "title": "Post 4: Introdução ao Machine Learning",
            "categories": ["Machine Learning", "Inteligência Artificial"],
            "content": "Aqui discutimos o início no mundo do Machine Learning.",
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
            "created_at": created_at_posts[3],
            "updated_at": created_at_posts[3],
        },
        {
            "id": fake.uuid4(),
            "title": "Post 5: Como Aprender a Programar",
            "categories": ["Carreira", "Desenvolvimento Pessoal"],
            "content": "Este post oferece dicas para quem quer começar a programar.",
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
            "created_at": created_at_posts[4],
            "updated_at": created_at_posts[4],
        },
    ]

    return posts


def update_post_data() -> dict:
    return {
        "content": "Este post foi atualizado com novas dicas para quem quer começar a programar.",
        "categories": ["Carreira", "Desenvolvimento Pessoal", "Educação"],
    }


def comment_data() -> dict:
    return {"content": fake.text()}


def many_comments_data() -> list[dict]:
    created_at_comments = [
        datetime.combine(
            fake.date_between(start_date="-1y", end_date="+1w"),
            datetime.min.time(),
        ).timestamp()
        for _ in range(5)
    ]

    comments = [
        {
            "id": fake.uuid4(),
            "content": fake.text(),
            "created_at": created_at,
            "updated_at": created_at,
            "post_id": fake.uuid4(),
            "post_title": fake.sentence(),
            "author_id": fake.uuid4(),
            "author_username": fake.user_name(),
        }
        for created_at in created_at_comments
    ]

    return comments


def single_comment_update() -> str:
    return fake.text()
