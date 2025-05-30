from sqlalchemy import inspect

from blog_api.models import (  # noqa: F401  # pylint: disable=unused-import
    comments,
    posts,
    users,
)


def get_table_names(sync_conn):
    inspector = inspect(sync_conn)
    return inspector.get_table_names()
