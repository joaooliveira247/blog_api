import asyncio
from enum import Enum
from uuid import UUID

import uvicorn
from typer import Exit, Typer, echo

from blog_api.commands.app import app
from blog_api.commands.database import cli_update_user_role

app_cli = Typer()


class Role(str, Enum):
    admin = "admin"
    dev = "dev"
    user = "user"


@app_cli.command()
def update_role(user_id: UUID, role: Role):
    """
    Change user Role.
    """
    try:
        echo(f"⚠️ Changing user's role {user_id} to {role}")
        asyncio.run(cli_update_user_role(user_id, role))
        echo("✅ Role changed successfully!")
    except Exception as e:
        echo(f"Error: {e}")
        raise Exit(code=1)


@app_cli.command()
def run(host: str = "127.0.0.1", port: int = 8000):
    "Run blog API"
    uvicorn.run(app, host=host, port=port)
