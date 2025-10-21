from fastapi import  APIRouter, Depends, HTTPException, Path
from starlette import status
from ..schemas import NoteRequest
from  ..models import Notes, User
from http import HTTPStatus
from typing import Annotated, List
from sqlmodel import Session
from ..database import engine
from .auth import get_current_user


def get_session():
    with Session(engine) as session:
        yield session

       
db_depencency = Annotated[Session, Depends(get_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter()



@router.get("/list_notes_by_user", status_code= status.HTTP_200_OK)
async def read_all(user:user_dependency, db: db_depencency):
    #session.exec(select(Hero).offset(offset).limit(limit)).all()
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")
    return db.query(Notes).filter(Notes.owner_id == user.get("id")).all()

@router.get("/all_notes", response_model = List[NoteRequest])
def get_shared_notes(user:user_dependency, db:db_depencency):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Authentication Failed')
    notes = db.query(Notes).filter(
        or_(
            Notes.owner_id == user.get("id"),
            Notes.shared_owner.any(User.id == user.get("id"))
        )
    ).all()
    return notes
    
@router.get("/note/{note_id}", status_code= status.HTTP_200_OK)
async def read_note(user: user_dependency, db: db_depencency, note_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")
    
    note_model = db.query(Notes).filter(Notes.id == note_id).\
        filter(Notes.owner_id == user.get("id")).first()
    if note_model is not None:
        return note_model
    raise HTTPException(status_code=404, detail='note not found')

@router.post("/note", response_model = NoteRequest, status_code=status.HTTP_201_CREATED)
async def create_note(user: user_dependency, db: db_depencency, note_request: NoteRequest):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")
    
    note_model = Notes(**note_request.model_dump(), owner_id = user.get('id'))
    db.add(note_model)
    db.commit()
    db.refresh(note_model)
    return note_model


@router.put("/note/{note_id}", status_code=HTTPStatus.NO_CONTENT)
async def update_note(user:user_dependency,
                      db:db_depencency, 
                      note_request:NoteRequest, 
                      note_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")
    note_model = db.query(Notes).filter(Notes.id == note_id).\
        filter(Notes.owner_id == user.get("id")).first()
    if note_model is None:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_model.title = note_request.title
    note_model.description = note_request.description
    
    db.add(note_model)
    db.commit()
    db.refresh(note_model)


@router.delete("/note/{note_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_note(user:user_dependency, db:db_depencency, note_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated")
    note_model = db.query(Notes).filter(Notes.id == note_id).\
        filter(Notes.owner_id == user.get("id")).first()
    if note_model is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.query(Notes).filter(Notes.id == note_id).\
        filter(Notes.owner_id == user.get("id")).delete()
    db.commit()
    
    
@router.post("/note/{note_id}/share/{target_username}")#, response_model=NoteRequest)
def share_note(note_id: int, target_username: str, user:user_dependency, db: db_depencency):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Authentication Failed')
    note_model = db.get(Notes, note_id)
    target = db.query(User).filter(User.user_name == target_username).first()
    if not note_model or not target:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Note or sharing user not found")
    if target in note_model.shared_owner:
        return {"Message" : f"Already shared with user {target.user_name}"}

    note_model.shared_owner.append(target)
    db.commit()
    db.refresh(note_model)
    return {"message": f"Note '{note_model.title}' successfully shared with {target.user_name}"}


@router.put("/note/{note_id}/unshare/{target_username}")
def unshare_note(note_id: int, target_username: str, user:user_dependency, db: db_depencency):
    if user is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Authentication Failed')
    note_model = db.get(Notes, note_id)
    target = db.query(User).filter(User.user_name == target_username).first()
    if not note_model or not target:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Note or sharing user not found")
    if target in note_model.shared_owner:
        note_model.shared_owner.remove(target)
        db.commit()
        db.refresh(note_model)
    return {"message": f"Note '{note_model.title}' successfully unshared with {target.user_name}"}




