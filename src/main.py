from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from src.core.database import engine
from src.features.home.router import router as home_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables are created on startup (Temporary until you setup Alembic)
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

# Mount the static folder so the browser can download output.css
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Include the vertical slices
app.include_router(home_router)
