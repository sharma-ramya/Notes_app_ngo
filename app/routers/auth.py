
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from ..models import User
from ..schemas import CreateUserRequest, Token
from http import HTTPStatus
from passlib.context import CryptContext
from ..database import engine
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

bcrypt_context = CryptContext(
    schemes=["bcrypt"], deprecated = "auto"
)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

#to find a random string for key, run openssl rand -hex 32 on terminal
ALGORITHM = 'HS256'

def get_session():
    with Session(engine) as session:
        yield session

       
db_depencency = Annotated[Session, Depends(get_session)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail='Could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail='Could not validate user')
# #########remove this#############
# @router.get("/users")
# async def show_user_details(db:db_depencency):
#     return db.query(User).all()

@router.post('/', status_code = HTTPStatus.CREATED)
async def create_user(create_user_request:CreateUserRequest, db: db_depencency):
    create_user_model = User(
        email = create_user_request.email,
        user_name = create_user_request.user_name,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
    )
    
    db.add(create_user_model)
    db.commit()


@router.post('/token',)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_depencency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail='Could not validate user')
    token = create_access_token(user.user_name, user.id, timedelta(minutes=30))
    return {'access_token':token, 'token_type': 'bearer'}
    