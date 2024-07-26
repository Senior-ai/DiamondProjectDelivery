from ..core import app
from .endpoints import router

app.include_router(router)
