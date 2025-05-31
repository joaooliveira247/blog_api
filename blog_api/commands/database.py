from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI
from sqlalchemy import inspect, update

from blog_api.contrib.models import BaseModel
from blog_api.core.database import engine, get_session
from blog_api.models import (  # noqa: F401  # pylint: disable=unused-import
    comments,
    posts,
    users,
)
from blog_api.models.users import UserModel


def get_table_names(sync_conn):
    inspector = inspect(sync_conn)
    return inspector.get_table_names()


@asynccontextmanager
async def database_init_lifespan(app: FastAPI):
    # fix return type of this function
    async with engine.begin() as conn:
        existing_tables = await conn.run_sync(get_table_names)
        all_tables = BaseModel.metadata.tables.keys()

        for table in all_tables:
            if table not in existing_tables:
                print(f"✅ {table} created")

        await conn.run_sync(
            lambda sync_conn: BaseModel.metadata.create_all(bind=sync_conn)
        )

    yield


async def cli_update_user_role(user_id: UUID, role: str) -> None:
    async with get_session() as conn:
        await conn.execute(
            update(UserModel).where(UserModel.id == user_id).values(role=role)
        )
        await conn.commit()
