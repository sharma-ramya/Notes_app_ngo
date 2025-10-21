from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, relationship

# class Base(DeclarativeBase):
#     pass

notes_users = Table(
    "notes_users_association",
    Base.metadata,
    Column("notes_id", ForeignKey("notes.id"), primary_key=True),
    Column("users_id", ForeignKey("users.id"), primary_key=True),
)


class Notes(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    
    # owner_id = Column(Integer, ForeignKey("users.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="owned_notes")
    shared_owner = relationship("User", secondary=notes_users, back_populates="shared_notes")
    
    # owner = relationship("User", secondary= "notes_users_association", back_populates ="notes")
    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    user_name = Column(String, unique=True)
    first_name = Column(String)
    last_name  = Column(String)
    hashed_password  = Column(String)
    
    # notes = relationship("Notes", secondary= "notes_users_association",  back_populates = "owner")
    
    owned_notes = relationship("Notes", back_populates="owner")
    shared_notes = relationship("Notes", secondary=notes_users, back_populates="shared_owner")

    
    

    
 