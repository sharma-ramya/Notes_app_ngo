from pydantic import BaseModel, Field
from pydantic.networks import EmailStr
from typing import List, Optional
#from sqlmodel import SQLModel, Field

# class Note(SQLModel):
#     id: int | None = Field(default=None, primary_key=True)

# class Note(BaseModel):
#     pass

class UserBase(BaseModel):
    id: int
    email: EmailStr
    user_name: str
    
    model_config = {"from_attributes": True}

   
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str  
    shared_notes: Optional[List['NoteRequest']] = []
    
    model_config = {"from_attributes": True}
        

class NoteRequest(BaseModel):
    title : str = Field(min_length=3)
    description : str = Field(min_length=3, max_length=100)
    shared_owner : Optional[List['UserBase']] = []

    model_config = {"from_attributes": True}
  
class CreateUserRequest(BaseModel):
    email: EmailStr
    user_name: str
    first_name: str
    last_name: str
    password: str
    notes: List['NoteRequest'] = []
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
# This is necessary for a circular relationship to resolve correctly
NoteRequest.model_rebuild()
UserResponse.model_rebuild()
