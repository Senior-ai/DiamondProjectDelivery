from ..router import router


@router.get('/alive', status_code=200)
async def get_all_stones() -> bool:
    return True
