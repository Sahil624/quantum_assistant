from fastapi import FastAPI, Depends
from starlette.middleware import Middleware
from fastapi.staticfiles import StaticFiles

from server.core.config import config
from server.core.logging.logging import Logging


def make_middleware() -> list[Middleware]:
    middleware = []
    return middleware


def init_rotes(app: FastAPI):
    pass


def add_static_routes(app: FastAPI):
    app.mount("/static", StaticFiles(directory="server/static"), name="static")
    app.mount("/notebook", StaticFiles(directory="server/static/notebooks"), name="lo")


def print_routes(app: FastAPI):
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]

    print(url_list)


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

    add_static_routes(app_)
    init_rotes(app_)

    print_routes(app_)
    return app_
