"""Uygulamanın giriş noktası: uvicorn app.main:app"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.database import Base, SessionLocal, engine
from app.hatalar import BulunamadiHatasi, IsKuraliHatasi
from app.katalog import models as _katalog_models  # noqa: F401
from app.odunc_islemleri import models as _odunc_models  # noqa: F401
from app.ornek_veri import ornek_veri_yukle
from app.uyelik import models as _uyelik_models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if os.getenv("ORNEK_VERI", "1") == "1":
        with SessionLocal() as db:
            ornek_veri_yukle(db)
    yield


app = FastAPI(title="Online Kütüphane API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IsKuraliHatasi)
async def is_kurali_hatasi(_: Request, hata: IsKuraliHatasi):
    return JSONResponse(status_code=400, content={"detail": str(hata)})


@app.exception_handler(BulunamadiHatasi)
async def bulunamadi_hatasi(_: Request, hata: BulunamadiHatasi):
    return JSONResponse(status_code=404, content={"detail": str(hata)})


app.include_router(router)
