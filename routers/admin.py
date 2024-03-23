from fastapi import APIRouter, HTTPException, Path, Depends
from pydantic import BaseModel , Field
from models import Tasks
from starlette import status
from database import db_dependecy
from typing import Annotated
from .auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix="/admin",
    tags=['admin']
)


@router.get("/task", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependecy):
    print(user)
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(Tasks).all()