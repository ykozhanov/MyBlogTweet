from contextlib import asynccontextmanager
from typing import AsyncGenerator

from database.database import engine
from fastapi import FastAPI
from routes.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")
