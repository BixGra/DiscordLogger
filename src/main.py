import asyncio

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.utils.dependencies import discord_client
from src.routers import (
    logging_router,
    monitoring_router,
)
from src.utils.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(discord_client.start(get_settings().discord_token))
    await monitoring_router.get_graphs()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(logging_router.router)
app.include_router(monitoring_router.router)


@app.get("/")
async def root():
    return "DiscordLogger"
