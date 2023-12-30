import os
# from http.client import HTTPException
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from jose import jwt, JWTError
from datetime import datetime, timedelta
import logging, sys


load_dotenv()
logger = logging.getLogger("app_logger")
logger.addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(
    prefix='/auth',
    tags=["Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY")
print("secret_key", os.getenv("SECRET_KEY"))
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")



class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authinticate_user(email: str, password: str, db):
    print(f"========================== email : {email} pw - {password} ==============")
    user = db.query(User).filter(User.username == email).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    # return True
    return user


def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    print(f"===================== uid {user_id} | username {username} | timedelta {timedelta}")
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    # print(f"=============== secret key {SECRET_KEY} =============")
    return jwt.encode(claims=encode, key=SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        print(f"token {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user")
        return {"username": username, "id": user_id}
    except JWTError:
        # When authorizing using a button and trying to use other functions,
        # it gives this error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")



@router.post("/register")
async def create_user(create_user_request: CreateUserRequest, db: Session = Depends(get_db)):
    try:
        db_user = User(
            email=create_user_request.email,
            username=create_user_request.username,
            firstname=create_user_request.first_name,
            lastname=create_user_request.last_name,
            hashed_password=bcrypt_context.hash(create_user_request.password)
        )
        db.add(db_user)
        db.commit()
        return Response(content="Registration successful", status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"got error - {str(e)}")
        print("Got error =======", str(e))
        return Response(content=f"Got error - {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authinticate_user(form_data.username, form_data.password, db)
    if not user:
        #return 'Failed Authentication'
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
    # return 'Successfully Authinticated'


# def get_current_user():
#     return None
