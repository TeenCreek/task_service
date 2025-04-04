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


@app.get('/')
async def welcome():
    return {'message': 'Welcome to Async Task Service'}


app.include_router(tasks.router)


@app.get('/health')
async def health_check():
    return {'status': 'ok'}


add_pagination(app)
