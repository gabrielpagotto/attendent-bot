import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.routes import api_router
from src.database import create_db_and_tables

print(sys.getdefaultencoding())

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
