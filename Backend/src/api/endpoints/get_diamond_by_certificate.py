from typing import Union, Optional
from fastapi import Depends, HTTPException, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...services.diamonds import filter_diamond_by_certificate
from ...database.loader import sessionmaker
from ..router import router
from ...core import BACKEND_ACCESS_TOKEN

bearer = HTTPBearer()


@router.get('/get_diamond_by_certificate', response_model=dict[str, Optional[Union[int, float, str, list[int]]]])
async def get_diamond_by_certificate(
        certificate: str = Path(..., description="cert"),
        token: HTTPAuthorizationCredentials = Depends(bearer)
) -> dict[str, Optional[Union[int, float, str, list[int]]]]:
    if token.credentials != BACKEND_ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

    async with sessionmaker() as session:
        diamond = await filter_diamond_by_certificate(session, certificate)
        if diamond is None:
            raise HTTPException(status_code=404, detail="Diamond not found")
        return diamond
