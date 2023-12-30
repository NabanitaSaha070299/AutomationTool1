import uvicorn
from fastapi import FastAPI,HTTPException,Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel ,Field
from passlib.context import CryptContext
import uvicorn
import sys,os
import database
# from .database import Base,SessionLocal,engine
from auth import router as AuthRouter
from todos import router as TodosRouter
from  user import router as userrouter
import models
from models import Todos
#some comment

app = FastAPI()
app.include_router(AuthRouter)
app.include_router(TodosRouter)
app.include_router(userrouter)
print("=============== os.")

#app = FastAPI()
#app.include_router(TodosRouter)
#print("=============== os.")

bcrypt_context=CryptContext(schemes=["bcrypt"])

def receive_signal(signalNumber, frame):
    print('Received:', signalNumber)
    sys.exit()


@app.on_event("shutdown")
async def startup_event():
    import signal
    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks

database.Base.metadata.create_all(database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model
class SignupModel(BaseModel):
    email: str
    password: str = Field(min_length=50)
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "email": "demo@email.com",
    #                 "password": "123456",
    #                 "first_name": "first_name",
    #                 "last_name": "last_name"
    #             }
    #         ]
    #     }
    # }
''''class TodoModel(BaseModel):
    Topic: str = Field(max_length=20)
    Ratings: int = Field(gt=0, lt=5)
    EmailAddress: str = Field(man_length=40)
    '''''


#@app.get('/getallusers')
#def getallusers(db : Session = Depends(get_db)):
 #   return db.query(models.User).all()


# @app.post('/signup',tags=["User Authentication"], description="User Signup")
# def signup(user: SignupModel, db: Session = Depends(get_db)):
#     try:
#         db_user = models.User(
#             email=user.email,
#             #password=user.password,
#             hashed_password=bcrypt_context.hash(user.password),
#             firstname=user.first_name,
#             lastname=user.last_name
#         )
#         user_id = db_user.id
#         db.add(db_user)
#         db.commit()
#         return {"status" : "success", "message" : f"The user {user_id} has been successfully registered"}
#     except HTTPException as e:
#         return {"status" : "failure", "message" : str(e)}



if __name__ == "__main__":
    print("==========", os.getcwd())
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, log_level="debug")