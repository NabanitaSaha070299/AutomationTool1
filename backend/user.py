from pathlib import Path

import fastapi
import uvicorn
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import  JSONResponse
# from fastapi.dependencies import models
import models

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
# from starlette import status

from auth import get_current_user
#from backend import models
from database import SessionLocal
# import models
from models import User
from models import Todos  # Todos
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt
from auth import get_current_user

# from .auth import get_current_user, router


router = APIRouter(
    prefix='/users',
    tags=["users"]
)

class ResponseModelUpdate(BaseModel):
    status : object
    message : str

response_schema_update_user= {
    201 : {
            "model" : ResponseModelUpdate,
            "description": "Successfully updated",
            "content": {"application/json": {
                "example": {"status": 201, "value": "Successfully updated user"}
            }}
    },
    500: {
            "model" : ResponseModelUpdate,
            "description": "Internal server error",
            "content": {"application/json": {
                "example": {"status": 500, "value": "Got error"}
            }},
    }
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class UserRequest(BaseModel):
    # id: int
    username: str
    email : str
    firstname : str
    lastname : str
    # EmailAddress : str

@router.get("/getallusers", status_code=status.HTTP_200_OK)
async def getallusers(user: user_dependency, db: db_dependency):
    result=[]
    users= db.query(models.User).all()
    for user in users:
        result.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname
            }
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)



    #return [
     #   User(id="", email=""),
      #  User(firstname="", lastname="")
    #]

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def getuserbyid(user: user_dependency,db: db_dependency, user_id: int = Path(gt=0)):
  try:
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')

    user_model =db.query(models.User).filter(User.id == user_id).first()
    if user_model is not None:
        return user_model
  except Exception as e:
      return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"error found - {e}")
@router.put("/user/{user_id}",status_code=status.HTTP_201_CREATED, responses=response_schema_update_user)
async def update_user(user: user_dependency, user_request:UserRequest, db: db_dependency):
    # check if user exists -> user_id
    try:
        if user is None:
            raise HTTPException(status_code=401,detail='Authentication Failed')

        user_model = db.query(models.User).first()
        if user_model is None:
            raise HTTPException(status_code=404, detail='User not found.')

        user_model.email = user_request.email
        user_model.firstname = user_request.firstname
        user_model.lastname = user_request.lastname

        db.add(user_model)
        db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content="Successfully updated user")
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Got error - {e}")

@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db:db_dependency,user_id: int =Path(gt=0)):
    try:
        if user is None:
            raise HTTPException(status_code=401,detail='Authentication Failed')

        user_model=db.query(models.User).first()
        if user_model is None:
            raise  HTTPException(status_code=404, detail='Todo not found.')
        db.query(models.User).delete()

        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content="Successfully deleted")

    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"error detected - {e}")

