from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

#sqlite_file_name = "database.db"
# #for sqlite
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./Notes_app_ngo/notesapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)

# for postgres

engine = create_engine(os.getenv("SQLALCHEMY_DATABASE_URL"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
