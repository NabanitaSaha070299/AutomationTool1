# from .database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
# from .database import Base
import database
class User(database.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=20), unique=True, index=True)
    password = Column(String(length=20))
    firstname = Column(String(length=20))
    lastname = Column(String(length=20))