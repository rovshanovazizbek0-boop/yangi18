import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .bot.bot import main as run_bot
from .config import (
    FRONTEND_ORIGIN,
    MEDIA_DIR,
    RUN_BACKGROUND_SERVICES,
    validate_production_settings,
)
from .database import Base, SessionLocal, engine
from .pipeline import run_pipeline
from .routers import admin, categories, news
from .seed import seed_categories


async def pipeline_loop_task():
    await asyncio.sleep(15)
    while True:
        try:
            loop = asyncio.get_running_loop()
            saved = await loop.run_in_executor(None, run_pipeline, 5)
            print(f"Pipeline yakunlandi: {saved} ta maqola saqlandi.")
        except Exception as error:
            print(f"Pipeline xatosi: {error}")
        await asyncio.sleep(int(os.getenv("PIPELINE_INTERVAL", "3600")))


async def bot_task():
    await asyncio.sleep(5)
    try:
        await run_bot()
    except Exception as error:
        print(f"Telegram bot xatosi: {error}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_settings()
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()

    background_tasks = []
    if RUN_BACKGROUND_SERVICES:
        background_tasks.append(asyncio.create_task(pipeline_loop_task()))
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            background_tasks.append(asyncio.create_task(bot_task()))
    yield

    for task in background_tasks:
        task.cancel()
    if background_tasks:
        await asyncio.gather(*background_tasks, return_exceptions=True)


app = FastAPI(
    title="AI News Uzbekistan API",
    description="Sun'iy intellekt yangiliklari — o'zbek tilida",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000", "https://yangi18.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(categories.router)
app.include_router(admin.router)

Path(MEDIA_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/")
def root():
    return {"loyiha": "AI News Uzbekistan", "hujjatlar": "/docs"}
