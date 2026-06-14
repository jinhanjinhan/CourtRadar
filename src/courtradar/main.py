from fastapi import FastAPI

from courtradar.api.routes import router as api_router
from courtradar.db.session import create_db_tables


def create_app() -> FastAPI:
    app = FastAPI(title="CourtRadar", version="0.1.0")
    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event() -> None:
        # Table creation is kept optional so local startup does not depend on a live database.
        await create_db_tables()

    return app


app = create_app()
