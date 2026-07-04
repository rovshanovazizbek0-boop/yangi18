from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGIN
from .database import Base, SessionLocal, engine
from .routers import admin, categories, news
from .seed import seed_categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_categories(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AI News Uzbekistan API",
    description="Sun'iy intellekt yangiliklari — o'zbek tilida",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(categories.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"loyiha": "AI News Uzbekistan", "hujjatlar": "/docs"}
