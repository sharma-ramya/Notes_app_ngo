from fastapi import  APIRouter, Depends, HTTPException, Path
from ..models import User
from ..schemas import UserResponse
from http import HTTPStatus
from typing import Annotated, List
from sqlmodel import SQLModel, Session
from ..database import engine
from .auth import get_current_user
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from ..schemas import NoteRequest
from  ..models import Notes


class UserPasswordUpdate(SQLModel):
    password:str
    new_password: str
    
# class UserPhoneNumberUpdate(SQLModel):
#     phone_number: str


def get_session():
    with Session(engine) as session:
        yield session

       
db_depencency = Annotated[Session, Depends(get_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

router = APIRouter(
    prefix='/user',
    tags=['user']
)

@router.get('/information/', status_code=HTTPStatus.OK) #, response_model=UserResponse)
async def get_user_info(user: user_dependency, db:db_depencency):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(User).filter(user.get('id')==User.id).first()
    return user_model


@router.put('/update_password', status_code=HTTPStatus.NO_CONTENT)
async def update_password(user:user_dependency,
                          db: db_depencency, 
                          user_password_update: UserPasswordUpdate):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if not bcrypt_context.verify(user_password_update.password, user_model.hashed_password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Password verification failed")
    user_model.hashed_password = bcrypt_context.hash(user_password_update.new_password)
    db.add(user_model)
    db.commit()
    #db.refresh(user_model)
    
