from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request, status

from beacon.data.db import DBClient
from beacon.data.models import HostMetadata
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


async def get_paginated_host_metadata(
    request: Request, page: int = 1, page_size: int = 10
) -> list[HostMetadata]:
    db_client: DBClient = request.app.state.db
    offset = (page - 1) * page_size
    metadata_list = await db_client.get_paginated_host_metadata(
        offset=offset, limit=page_size
    )
    return metadata_list


app = FastAPI(lifespan=lifespan)
