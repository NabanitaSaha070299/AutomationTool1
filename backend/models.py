# from .database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
# from .database import Base
# import database
import database

class User(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=20), unique=True, index=True)
    email = Column(String(length=20), unique=True, index=True)
    hashed_password = Column(String(length=100))
    firstname = Column(String(length=20))
    lastname = Column(String(length=20))


class Todos(database.Base):
    __tablename__ = "SCRAPE_METADATA"

    id = Column(Integer, primary_key=True, index=True)
    TopicName = Column(String(length=50))
    Rating = Column(Float)
    Duration_From = Column(Float)
    Duration_upto = Column(Float)
    ItemMax=Column(Integer)
    EmailAddress = Column(String(length=25))
    owner_id = Column(Integer, ForeignKey("user.id"))


