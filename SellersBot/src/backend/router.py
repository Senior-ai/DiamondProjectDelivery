from fastapi import APIRouter
from ..core import fastapi_instance

router = APIRouter(prefix="/api/v1")
fastapi_instance.include_router(router)
