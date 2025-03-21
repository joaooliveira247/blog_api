from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from blog_api.core.database import get_session


DatabaseDependency: AsyncSession = Annotated[AsyncSession, Depends(get_session)]
