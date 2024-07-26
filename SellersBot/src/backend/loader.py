from ..core import fastapi_instance
from .endpoints import router

fastapi_instance.include_router(router)
