import uvicorn
from fastapi import FastAPI,HTTPException,Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel ,Field
import uvicorn
import sys,os
import database
# from .database import Base,SessionLocal,engine
import models

app = FastAPI()
print("=============== os.")

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
    password: str = Field(min_length=5)
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



@app.get('/getallusers')
def getallusers(db : Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post('/signup')
def signup(user: SignupModel, db: Session = Depends(get_db)):
    try:
        db_user = models.User(
            email=user.email,
            password=user.password,
            firstname=user.first_name,
            lastname=user.last_name
        )
        user_id = db_user.id
        db.add(db_user)
        db.commit()
        return {"status" : "success", "message" : f"The user {user_id} has been successfully registered"}
    except HTTPException as e:
        return {"status" : "failure", "message" : str(e)}
if __name__ == "__main__":
    print("==========", os.getcwd())
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, log_level="info")