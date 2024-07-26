from fastapi import APIRouter
from ..router import router


notify_router = APIRouter(prefix="/notify")


# Put /notify endpoints here


router.include_router(notify_router)
