from fastapi import FastAPI

from . import config
from .routers import init_router
from .models import init_db, create_all


def create_app():
    settings = config.get_settings()
    app = FastAPI()

    init_db(settings)

    init_router(app)

    @app.on_event("startup")
    async def on_startup():
        await create_all()

    return app
