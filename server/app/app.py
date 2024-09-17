from fastapi import FastAPI, Depends
from starlette.middleware import Middleware

from server.core.config import config
from server.core.logging.logging import Logging


def make_middleware() -> list[Middleware]:
    middleware = []
    return middleware


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="API",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    return app_
