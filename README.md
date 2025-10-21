# Notes App

### Setup
- setup the envionment variable with the following command:
```
source fastapi-venv/bin/activate
```

- You can run the app as:
```
uvicorn app.main:app --reload
```

- Go to [localhost/docs](http://127.0.0.1:8000/docs) for API endpoints.

- If you want to use a postgres based database, create a .env file and define the database URL as SQLALCHEMY_DATABASE_URL. It can also be a sqlite db (for sqlite db, a url is provided in the comments in database.py).

- Add your own SECRET_KEY in .env for password hashing algorithm. 
