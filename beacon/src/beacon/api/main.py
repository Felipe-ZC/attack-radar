from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status

from beacon.data.db import DBClient
from beacon.shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres = DBClient(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )
    await postgres.connect()
    app.state.db = postgres
    yield
    await postgres.disconnect()


app = FastAPI(lifespan=lifespan)
