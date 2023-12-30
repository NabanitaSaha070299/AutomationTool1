from pathlib import Path

import fastapi
import uvicorn
from typing import Annotated

from fastapi import APIRouter, Depends,HTTPException, status, Response
from fastapi.responses import  JSONResponse

from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
# from starlette import status

from auth import get_current_user
from database import SessionLocal
#import models
from models import User
from models import Todos #Todos
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt
#from .auth import get_current_user, router

'''router=APIRouter(
    prefix='/todos',
    tags=["Todos"])
'''
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    prefix='/todos',
    tags=["Todos"]
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    TopicName: str
    Rating: float
    Duration_From : float
    Duration_upto : float
    ItemMax : int
    EmailAddress : str


# @router.get("/",status_code=status.HTTP_200_OK)
# async def read_all(user: user_dependency,db: db_dependency, ):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication Failed')
#     return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

# from auth import authinticate_user,create_access_token,get_current_user
# from datetime import timedelta
# @router.post("/auth/token")
# async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#                                  db: db_dependency):
#     print(f"=============== {form_data.username} ====================")
#     user = authinticate_user(form_data.username, form_data.password, db)
#     if not user:
#         #return 'Failed Authentication'
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
#     token = create_access_token(user.username, user.id, timedelta(minutes=20))
#     return {"token" : token}
@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt=0)):
 try:
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')

    todo_model =db.query(Todos).filter(Todos.id == todo_id).\
        filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
 except Exception as e:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Got error - {e}")

#def HTTPException(detail):
  #  pass


# def HTTPException(status_code, detail):
#     pass


@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,db:db_dependency,
                      todo_request: TodoRequest):

 try:
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    todo_model=Todos(**todo_request.model_dump(),owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED, content="Successfully created todo")
 except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Got error - {e}")
@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,db: db_dependency,
                      todo_request:TodoRequest,
                      todo_id: int =Path(gt=0)):
 try:
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.Topic = todo_request.Topic
    todo_model.Ratings = todo_request.Ratings
    todo_model.EmailAddress = todo_request.EmailAddress

    db.add(todo_model)
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content="Successfully updated user")
 except Exception as e:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Got error - {e}")
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db:db_dependency,todo_id: int =Path(gt=0)):
 try:
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')

    todo_model=db.query(Todos).filter(Todos.id == todo_id)\
    .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise  HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()

    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content="Successfully deleted")

 except Exception as e:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"error detected - {e}")
