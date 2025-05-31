from enum import Enum

from typer import Typer

app = Typer()


class Role(str, Enum):
    admin = "admin"
    dev = "dev"
    user = "user"
