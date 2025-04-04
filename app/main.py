from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core.config import settings
from app.routers import tasks

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(tasks.router)

add_pagination(app)
