from passlib.context import CryptContext

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gen_hash(passwd: str) -> str:
    return pwd_context.hash(passwd)
