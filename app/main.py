from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import auth, notes, users
from .database import engine
from sqlalchemy import inspect
#from sqlmodel import SQLModel
from .models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    #SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(bind=engine)
    print("Database connected and tables created.")
    yield
    # Shutdown logic
    print("Application shutdown, resources cleaned up.")

app = FastAPI(lifespan=lifespan)

# Create an inspector object
inspector = inspect(engine)

# Get the list of all tables
tables = inspector.get_table_names()

# Print the list of tables
print("Tables in the database:")
for table in tables:
    print(table)
    
# @app.get("/healthy")
# def health_check():
#     return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(users.router)

