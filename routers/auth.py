from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import db_dependecy
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.identify(password, user.hashed_password):
        return False
    return user

def generate_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id,
        'user_role': role
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    print(f"This is a SECRET KEY:  {SECRET_KEY}")
    token = jwt.encode(encode, SECRET_KEY, algorithm = ALGORITHM)
    return token

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: int = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {
            'username': username,
            'id': user_id,
            'user_role': user_role
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    
class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependecy, user_request: UserRequest):
    create_user = Users(
        email = user_request.email,
        username = user_request.username,
        first_name = user_request.first_name,
        last_name = user_request.last_name,
        role = user_request.role,
        hashed_password = bcrypt_context.hash(user_request.password),
        is_active = True
    )
    db.add(create_user)
    return db.commit()

@router.post("/token", response_model=Token)
async def access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependecy):
    user = authenticate_user(form_data.username, form_data.password, db)
    if(not user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    token = generate_access_token(user.username, user.id, user.role,timedelta(minutes=20))
    return {
        'access_token': token,
        'token_type': "bearer"
    }