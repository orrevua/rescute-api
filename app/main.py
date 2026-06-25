from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.inbound.api.router import router


def create_app() -> FastAPI:
    app = FastAPI(title="Rescute API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()
