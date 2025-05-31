from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import inspect

from blog_api.contrib.models import BaseModel
from blog_api.core.database import engine
from blog_api.models import (  # noqa: F401  # pylint: disable=unused-import
    comments,
    posts,
    users,
)


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
