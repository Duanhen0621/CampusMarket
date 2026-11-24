from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import admin, auth, interaction, items, orders, reports, uploads
from app.routers.interaction import favorites_router

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = settings.upload_path
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

for module in (auth, items, interaction, orders, admin, reports, uploads):
    app.include_router(module.router, prefix=settings.api_v1_prefix)

app.include_router(favorites_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["System"])
def index():
    return {"code": 200, "msg": "campus market api", "data": {"docs": "/docs"}}


@app.get(f"{settings.api_v1_prefix}/health", tags=["System"])
def health():
    return {
        "code": 200,
        "msg": "success",
        "data": {"status": "ok", "app": settings.app_name, "version": app.version},
    }
