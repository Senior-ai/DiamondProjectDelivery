from typing import Union, Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...services.diamonds import get_all_diamonds_with_owners
from ...database.loader import sessionmaker
from ..router import router
from ...core import BACKEND_ACCESS_TOKEN

bearer = HTTPBearer()


@router.get('/get_all_stones', response_model=list[dict[str, Optional[Union[int, float, str, list[int]]]]])
async def get_all_stones(
        token: HTTPAuthorizationCredentials = Depends(bearer)
) -> list[dict[str, Optional[Union[int, float, str, list[int]]]]]:
    if token.credentials != BACKEND_ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    async with sessionmaker() as session:
        return await get_all_diamonds_with_owners(session)
