from fastapi import Depends
from sqlmodel import Session

from src.database import engine
from src.services import Services


def get_session():
    with Session(engine) as session:
        yield session


def get_services(session=Depends(get_session)) -> Services:
    return Services(session)
