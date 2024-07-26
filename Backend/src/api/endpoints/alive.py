from ..router import router


@router.get('/alive', status_code=200)
async def alive() -> bool:
    return True
