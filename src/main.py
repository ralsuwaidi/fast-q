from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sqlmodel import SQLModel

from core.database import engine
from core.logger import setup_logging
from features.hospitals.router import router as hospitals_router
from features.residents.router import router as residents_router
from features.users.router import router as users_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables are created on startup (Temporary until you setup Alembic)
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

# Mount the static folder so the browser can download output.css
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include the vertical slices
app.include_router(users_router)
app.include_router(residents_router)
app.include_router(hospitals_router)
